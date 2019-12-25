import asyncio
import aioredis
import numpy as np

from aiohttp import web
import socketio

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

"""Proof of concept to asynchronously run a slow asynchronous function with
a faster asynchronous function. Used to ensure that different apis can pass off
their turn non-blocking so that faster apis can update quicker at their own pace
while also integrating with sockets and aiohttp to update a webpage"""
async def socket_emit(stat_id, data):
    await sio.emit('response', {
            "stat_id" : '{}'.format(stat_id),
            'data': "{}".format(data)
            })

async def random_number_slow(stat_id):
    while True:
        pause_time = np.random.choice(range(0,10))
        print(pause_time)
        random_num = str(np.random.choice(range(0,1000)))
        print(random_num)
        await asyncio.sleep(5)
        print("SLOW", random_num)
        await socket_emit("SMALLSTAT1", random_num)

async def random_number_fast(stat_id):
    while True:
        pause_time = np.random.choice(range(0,10))
        print(pause_time)
        random_num = str(np.random.choice(range(0,1000)))
        print(random_num)
        await asyncio.sleep(1)
        print("FAST", random_num)
        await socket_emit("SMALLSTAT2", random_num)

async def main():
    slowTask = asyncio.create_task(random_number_slow("SMALLSTAT1"))
    fastTask = asyncio.create_task(random_number_fast("SMALLSTAT2"))

    await slowTask
    await fastTask
    
async def index(request):
    with open('ioclient.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    sio.start_background_task(main)
    web.run_app(app)