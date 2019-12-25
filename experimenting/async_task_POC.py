import asyncio
import aioredis
import numpy as np

"""Proof of concept to asynchronously run a slow asynchronous function with
a faster asynchronous function. Used to ensure that different apis can pass off
their turn non-blocking so that faster apis can update quicker at their own pace """
async def random_number_slow(stat_id):
    while True:
        pause_time = np.random.choice(range(0,10))
        print(pause_time)
        random_num = str(np.random.choice(range(0,1000)))
        print(random_num)
        await asyncio.sleep(5)
        print("SLOW", random_num)

async def random_number_fast(stat_id):
    while True:
        pause_time = np.random.choice(range(0,10))
        print(pause_time)
        random_num = str(np.random.choice(range(0,1000)))
        print(random_num)
        await asyncio.sleep(1)
        print("FAST", random_num)

async def main():
    slowTask = asyncio.create_task(random_number_slow("SMALLSTAT1"))
    fastTask = asyncio.create_task(random_number_fast("SMALLSTAT2"))

    await slowTask
    await fastTask
    


if __name__ == '__main__':
    asyncio.run(main())