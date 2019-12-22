import asyncio
import aioredis

"""Proof of concept to asynchronously listen to multiple data streams through redis subscriptions
and pass off the IOLoop to other functions that may need it as to not block """
async def reader(ch):
    """wait for new message on redis channel and allow IOLoop to run other async functions in the mean time"""
    while (await ch.wait_message()):
        msg = await ch.get()
        print("Got Message:", msg)

async def counter():
    """Increment counter by 1 and print, then await for 1 second to allow other async functions to run"""
    count = 0
    while True:
        print(count)
        count+=1
        await asyncio.sleep(.000000001)

async def main():
    sub = await aioredis.create_redis(
        'redis://localhost')
    channel1Sub = await sub.subscribe('channel1')
    channel2Sub = await sub.subscribe('channel2')
    
    channel1 = channel1Sub[0]
    channel2 = channel2Sub[0]

    subTask1 = asyncio.create_task(reader(channel1))
    countTask = asyncio.create_task(counter())
    subTask2 = asyncio.create_task(reader(channel2))

    await subTask1
    await countTask
    await subTask2
    sub.close()


if __name__ == '__main__':
    asyncio.run(main())