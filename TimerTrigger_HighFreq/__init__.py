import asyncio
import logging as fellerbuncher
import azure.functions as func

from datetime import datetime, timedelta, timezone
from dateutil import tz
from contextlib import asynccontextmanager

from api_bestbuy_async import bb_main
from .config import get_queries

@asynccontextmanager
async def get_event_loop():
    """Context manager for event loop handling"""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        yield loop
    finally:
        loop.close()


def main(mytimer: func.TimerRequest) -> None:
    fellerbuncher.info('ACTION!'.center(20, "*"))

    # Get last update time in Central timezone
    local_time = (datetime.now(timezone.utc) - timedelta(minutes=16)) \
                  .astimezone(tz.gettz('US/Central'))
    LAST_UPDATE_DATE = local_time.strftime('%Y-%m-%dT%H:%M:%S')

    # Get queries and fetch results
    queries = get_queries(LAST_UPDATE_DATE)
    
    async def run_tasks():
        async with get_event_loop() as loop:
            tasks = [
                bb_main(email=True,**q) 
                for q in queries.values()
            ]
            await asyncio.gather(*tasks)
            fellerbuncher.info(f'Timer trigger completed at {local_time}')

    asyncio.run(run_tasks())
