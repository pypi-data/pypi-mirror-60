'''Custom 'publish only' redis client which uses redis PIPELINING

Copyright (c) 2020 Machine Zone, Inc. All rights reserved.
'''

import asyncio
from urllib.parse import urlparse
from typing import Optional

import hiredis


class RedisClient(object):
    '''
    See https://redis.io/topics/mass-insert
    '''
    def __init__(self, url, password, verbose=False):

        netloc = urlparse(url).netloc
        host, _, port = netloc.partition(':')
        if port:
            port = int(port)
        else:
            port = 6379

        self.host = host
        self.port = port

        self.password = password
        self.verbose = verbose
        self.reset()
        self.lock = asyncio.Lock()

        self.read_size = 1024

    def reset(self):
        self.publishCount = 0

    async def connect(self):
        async with self.lock:
            print(f'Opening connection to redis at {self.host}:{self.port}')
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port)

            self._reader = hiredis.Reader()

        if self.password:
            self.writer.write(b'*2\r\n')
            self.writeString(b'AUTH')

            password = self.password
            if not isinstance(password, bytes):
                password = password.encode('utf8')

            self.writeString(password)
            await self.execute()

    async def readResponse(self):
        response = self._reader.gets()
        while response is False:
            try:
                buf = await self.reader.read(self.read_size)
            except asyncio.CancelledError:
                raise
            except Exception:
                e = sys.exc_info()[1]
                raise ConnectionError("Error {} while reading from stream: {}".format(type(e), e.args))
            if not buf:
                raise ConnectionError("Socket closed on remote end")
            self._reader.feed(buf)
            response = self._reader.gets()

        return response

    async def execute(self):
        async with self.lock:
            await self.writer.drain()

            results = []

            # read until we get something
            for i in range(self.publishCount):
                line = await self.reader.readline()
                results.append(line)

                # FIXME: proper error handling !!!
                if self.verbose:
                    print(f'Received: {line.decode()!r}')

                if 'NOAUTH Authentication required' in line.decode():
                    raise ValueError('Authentication failed')

            self.reset()

            return results

    def close(self):
        print('Close the connection')
        self.reset()
        self.writer.close()

    async def wait_closed(self):
        await self.writer.wait_closed()

    def publish(self, channel, msg):
        self.publishCount += 1

        if not isinstance(channel, bytes):
            channel = channel.encode('utf8')

        if not isinstance(msg, bytes):
            msg = msg.encode('utf8')

        self.writer.write(b'*3\r\n')
        self.writeString(b'PUBLISH')
        self.writeString(channel)
        self.writeString(msg)

    def writeString(self, data: bytes):
        # import pdb; pdb.set_trace()
        # data = data.encode('utf-8')

        self.writer.write(b'$%d\r\n' % len(data))
        self.writer.write(data)
        self.writer.write(b'\r\n')

    async def ping(self):
        self.writer.write(b'*1\r\n')
        self.writeString(b'PING')

        response = await self.readResponse()
        return response == b'PONG'

    async def exists(self, key):
        self.writer.write(b'*2\r\n')
        self.writeString(b'EXISTS')

        if not isinstance(key, bytes):
            key = key.encode('utf8')

        self.writeString(key)

        response = await self.readResponse()
        return response == 1

    async def xinfo(self, key, stream=True):
        self.writer.write(b'*3\r\n')
        self.writeString(b'XINFO')

        if stream:
            self.writeString(b'STREAM')

        if not isinstance(key, bytes):
            key = key.encode('utf8')

        self.writeString(key)

        response = await self.readResponse()
        return response

    async def xadd(self, key: str, attrName: str, attrValue: str, maxLen: int):
        self.writer.write(b'*8\r\n')
        self.writeString(b'XADD')
        self.writeString(key.encode())

        # should be optional
        self.writeString(b'MAXLEN')
        self.writeString(b'~')
        self.writeString(str(maxLen).encode())

        self.writeString(b'*')
        self.writeString(attrName.encode())
        self.writeString(attrValue.encode())

        response = await self.readResponse()
        return response

    async def xread(self, key, latest_id):
        '''
        Result set is a list
        [[b'1580684995724-0', [b'temperature', b'10']]]
        '''
        self.writer.write(b'*6\r\n')
        self.writeString(b'XREAD')
        self.writeString(b'BLOCK')
        self.writeString(b'0')
        self.writeString(b'STREAMS')

        if not isinstance(key, bytes):
            key = key.encode('utf8')
        self.writeString(key)

        if not isinstance(latest_id, bytes):
            latest_id = latest_id.encode('utf8')
        self.writeString(latest_id)

        response = await self.readResponse()

        items = []
        for item in response[0][1]:
            position = item[0]
            array = item[1]
            entries = {}

            for i in range(len(array) // 2):
                key = array[2*i]
                value = array[2*i + 1]
                entries[key] = value

            items.append((position, entries))

        return items


async def create_redis_publisher(host, port, password, verbose=False):
    client = RedisClient(host, port, password, verbose)
    await client.connect()
    return client
