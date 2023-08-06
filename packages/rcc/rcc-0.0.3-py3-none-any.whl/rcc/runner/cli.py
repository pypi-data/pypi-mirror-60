'''CLI

Copyright (c) 2020 Machine Zone, Inc. All rights reserved.
'''

import asyncio
import sys

import click
from rcc.client import RedisClient


async def interpreter(redis_url, redis_password):
    client = RedisClient(redis_url, redis_password)
    await client.connect()

    while True:
        line = input('> ')

        args = line.split()
        cmd = args[0]
        cmd = cmd.upper()

        if cmd == 'DEL':
            key = args[1]
            response = await client.delete(key)
            print(response)

        elif cmd == 'XREVRANGE':
            key = args[1]
            end = args[2]
            start = args[3]
            COUNT = args[4]
            count = args[5]
            print(locals())
            response = await client.xrevrange(key, end, start, count)
            print(response)


@click.command()
@click.option('--redis_url', default='redis://localhost')
@click.option('--redis_password')
def cli(redis_url, redis_password):
    '''Publish to a channel
    '''

    asyncio.get_event_loop().run_until_complete(
        interpreter(redis_url, redis_password)
    )
