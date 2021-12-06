import aiohttp
import asyncio
import json


async def fetch(session):
    url = f"https://api.bestbuy.com/v1/products"
    payload = {
                "apiKey": "AwGV1zCqy6FDoQHNUoNcfjqA",
                "pageSize": 100,
                "format": "json",
                "show": "all",
                "page": 1
            }

    # async with aiohttp.ClientSession() as session:
    async with session.get(url, params=payload) as resp:
        data = json.dumps(await resp.json(), indent=4)
        # print(json.dumps(data, indent=4))

    return data

async def main():
    async with aiohttp.ClientSession() as session:
        data = await fetch(session)
        print(data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # loop.run_until_complete(asyncio.gather(*(get_player(*args) for args in player_args)))

