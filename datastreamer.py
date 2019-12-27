import asyncio
import aioredis
import requests
import time

async def main():
    """Connect to redis and publish responses from api calls from worldclockapi every 5 seconds"""
    pub = await aioredis.create_redis(
            'redis://localhost')
    
    while True:
        response = requests.get("http://worldclockapi.com/api/json/utc/now")
        response_json = response.json()
        curr_time = response_json["currentFileTime"]
        res = await pub.publish_json('SMALLSTAT1', curr_time)
        #print(response_json)
        ##print(curr_time)
        await asyncio.sleep(5)
if __name__ == '__main__':
    asyncio.run(main())
