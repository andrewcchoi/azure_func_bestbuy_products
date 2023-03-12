import datetime
import logging

import azure.functions as func

from TimerTrigger1.api_bestbuy_async_discount_alert import bb_main


def main(mytimer: func.TimerRequest) -> None:

    logging.info('ACTION!'.center(20, "*"))
    bb_main()
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
