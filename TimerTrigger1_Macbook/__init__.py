import os
import datetime
import logging
import asyncio
import azure.functions as func

from typing import List
from dateutil import tz
from datetime import datetime, timedelta

from api_bestbuy_async import bb_main

def async_call(url: str, email: bool=True) -> None:
    """Makes an asynchronous call to a given URL.

    :param url: The URL to call.
    :param email: Whether to send an email notification after the call. Defaults to True.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bb_main(url=url, email=email))


def main(mytimer: func.TimerRequest) -> None:
    """Runs a Python timer trigger function.

    This function logs an action message, gets the current date and time in UTC and US/Pacific zones,
    formats the date and time as a string, calls two URLs asynchronously using the async_call function,
    and logs the timer status and the UTC timestamp.

    Args:
        mytimer (func.TimerRequest): A timer request object.

    Raises:
        Exception: If any error occurs during the execution of the function.
    """

    logging.info('ACTION!'.center(20, "*"))

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Pacific')

    utc = datetime.utcnow() - timedelta(minutes=1441) # * utc time 1_441 minutes (24hrs and 1 min) before
    utc_timestamp = utc.replace(tzinfo=from_zone) # * explicitly apply utc timezone
    local = utc_timestamp.astimezone(to_zone) # * convert to local time

    LAST_UPDATE_DATE = local.strftime('%Y-%m-%dT%H:%M:%S') # * apply string format to date timestamp
    urls: List[str] = [
        "https://api.bestbuy.com/v1/products(department=COMPUTERS&class=APPLE LAPTOP&orderable=Available&onlineAvailability=trueonSale=true&active=true&manufacturer=Apple)", 
        "https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&orderable=Available&onlineAvailability=true&active=true&onSale=true&details.value=nvidia)"
        ]

    # macbook and nvidia pcs deals
    for url in urls:
        async_call(url=url)
    
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

'''
resources: 
https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
'''
