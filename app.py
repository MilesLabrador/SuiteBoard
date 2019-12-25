import asyncio
import aioredis
import numpy as np

from aiohttp import web
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

async def socket_emit(stat_id, data):
    """Emit to socket with payload of stat_id and data in order for the
    front end to be able to update the correct elements with emitted data
    """
    await sio.emit('response', {
            "stat_id" : '{}'.format(stat_id),
            'data': "{}".format(data)
            })
"""Asynchronously listen to multiple data streams through redis subscriptions
and pass off the IOLoop to other functions that may need it as to not block
"""
async def listener(stat_id, ch):
    """wait for new message on redis channel and allow IOLoop to run other async functions in the mean time
    Parameters:
    stat_id (String) id of element to be updated on frontend
    ch (Channel) channel to subscribe to
    """
    while (await ch.wait_message()):
        msg = await ch.get()
        print("Got Message:", msg)
        await socket_emit(stat_id, msg)

async def main():
    sub = await aioredis.create_redis(
        'redis://localhost')
    channel1Sub = await sub.subscribe('channel1')
    channel2Sub = await sub.subscribe('channel2')
    
    channel1 = channel1Sub[0]
    channel2 = channel2Sub[0]

    subTask1 = asyncio.create_task(listener("SMALLSTAT1", channel1))
    subTask2 = asyncio.create_task(listener("SMALLSTAT2", channel2))

    await subTask1
    #await countTask
    await subTask2
    
async def index(request):
    with open('templates/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    sio.start_background_task(main)
    web.run_app(app)