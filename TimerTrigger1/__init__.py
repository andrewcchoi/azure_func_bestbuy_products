import datetime
import logging
import asyncio

import azure.functions as func

from TimerTrigger1.api_bestbuy_async_discount_alert import bb_main

LAST_UPDATE_DATE = '2023-03-11T17:53:43'

def main(mytimer: func.TimerRequest) -> None:
    global LAST_UPDATE_DATE
    logging.info('ACTION!'.center(20, "*"))
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    max_price_date = loop.run_until_complete(bb_main(last_update_date=LAST_UPDATE_DATE))
    LAST_UPDATE_DATE = max_price_date[0]
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
