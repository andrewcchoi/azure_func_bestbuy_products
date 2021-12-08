import aiohttp
import asyncio
import json


# async def fetch(session):
async def main():
    url = f"https://api.bestbuy.com/v1/products"
    payload = {
                "apiKey": "{}",
                "pageSize": 100,
                "format": "json",
                "show": "all",
                "page": 1
            }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=payload) as resp:
            data = await resp.json()
        print(resp.status)
        # print(json.dumps(data, indent=4))

    print(type(json.dumps(data))) # str
    print(type(data)) # dict
    return data

    # async with aiohttp.ClientSession() as session:
    # data = await fetch()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    # loop.run_until_complete(asyncio.gather(*(get_player(*args) for args in player_args)))

