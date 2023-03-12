import datetime
import logging
import asyncio

import azure.functions as func

from TimerTrigger1.api_bestbuy_async_discount_alert import bb_main


def main(mytimer: func.TimerRequest) -> None:

    logging.info('ACTION!'.center(20, "*"))
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bb_main())

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
