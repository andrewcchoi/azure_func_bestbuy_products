import os
import datetime
import logging
import asyncio
import azure.functions as func

from typing import Dict
from dateutil import tz
from datetime import datetime, timedelta

from api_bestbuy_async import bb_main

def async_call(url: str, subject: str, email: bool=False) -> None:
    """Makes an asynchronous call to a given URL.

    :param url: The URL to call.
    :type url: str
    :param subject: The subject of the email notification.
    :type subject: str
    :param email: Whether to send an email notification after the call. Defaults to False.
    :type email: bool

    .. code-block:: python

        # Example of using async_call function
        url = "https://api.bestbuy.com/v1/products(longDescription=iPhone*|sku=7619002)"
        subject = "Best Buy Deals"
        email = True
        df, df_shape = async_call(url, subject, email)
        print(df)
        print(df_shape)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bb_main(url=url, subject=subject, email=email))


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

    # Define a type alias for the inner dictionary
    Query = Dict[str, str]

    # Use the type alias for the outer dictionary
    queries: Dict[str, Query] = {
        "macbook": {
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=macbook*&details.value!=intel*&orderable=Available&onlineAvailability=true&onSale=true&active=true)",
            "subject": f'HttpTrigger1_Macbook - Best Buy Deals ({datetime.now()})'
        },
        "nvidia": {
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*)",
            "subject": f'HttpTrigger1_Nvidia_Pc - Best Buy Deals ({datetime.now()})'
        }
    }
    # macbook and nvidia pcs deals
    for query in queries.keys():
        async_call(url=queries[query]["url"], subject=queries[query]["subject"], email=True)
    
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

'''
resources: 
https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
'''
