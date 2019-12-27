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
        msg_decoded = msg.decode("utf-8") # Convert bytes to utf-8 character set
        print("Got Message:", msg_decoded)
        await socket_emit(stat_id, msg_decoded)

async def main():
    sub = await aioredis.create_redis(
        'redis://localhost')
    SMALLSTAT1_sub = await sub.subscribe('SMALLSTAT1')
    SMALLSTAT2_sub = await sub.subscribe('SMALLSTAT2')
    
    SMALLSTAT1_channel = SMALLSTAT1_sub[0]
    SMALLSTAT2_channel = SMALLSTAT2_sub[0]

    SMALLSTAT1_task = asyncio.create_task(listener("SMALLSTAT1", SMALLSTAT1_channel))
    SMALLSTAT2_task = asyncio.create_task(listener("SMALLSTAT2", SMALLSTAT2_channel))

    await SMALLSTAT1_task
    await SMALLSTAT2_task
    
async def index(request):
    with open('templates/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    sio.start_background_task(main)
    web.run_app(app)