import os
import datetime
import logging
import asyncio
import azure.functions as func

from typing import Dict, List
from dateutil import tz
from datetime import datetime, timedelta

from api_bestbuy_async import bb_main

def async_call(
        url: str
        , subject: str
        , columns: List=None
        , detail_names: List=None
        , offers: List=None
        , email: bool=False
        ) -> None:
    """Makes an asynchronous call to a given URL.

    :param url: The URL to call.
    :type url: str
    :param subject: The subject of the email notification.
    :type subject: str
    :param columns: List of columns to extract from response.
    :type columns: List
    :param detail_names: List of details to extract from response.
    :type detail_names: List
    :param offers: List of offer start and end date to extract from response.
    :type offers: List
    :param email: Whether to send an email notification after the call. Defaults to False.
    :type email: bool

    .. code-block:: python

        # Example of using async_call function
        url = "https://api.bestbuy.com/v1/products(longDescription=iPhone*|sku=7619002)"
        subject = "Best Buy Deals"
        email = True
        df, df_shape = async_call(url, subject, columns, detail_names, offers, email)
        print(df)
        print(df_shape)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        bb_main(
            url=url
            , subject=subject
            , columns=columns
            , detail_names=detail_names
            , offers=offers
            , email=email
        )
    )


def main(mytimer: func.TimerRequest) -> None:

    logging.info('ACTION!'.center(20, "*"))

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Central')

    utc = datetime.utcnow() - timedelta(minutes=16) # * utc time 1_441 minutes (24hrs and 1 min) before
    utc_timestamp = utc.replace(tzinfo=from_zone) # * explicitly apply utc timezone
    local = utc_timestamp.astimezone(to_zone) # * convert to local time

    LAST_UPDATE_DATE = local.strftime('%Y-%m-%dT%H:%M:%S') # * apply string format to date timestamp
    # LAST_UPDATE_DATE = '2023-09-01T00:00:00'

    # Define a type alias for the inner dictionary
    Query = Dict[str, str]

    # Use the type alias for the outer dictionary
    queries: Dict[str, Query] = {
        # "nvidia": {
        #     "url":f"https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&salePrice<1000&priceUpdateDate>{LAST_UPDATE_DATE}&orderable=Available&onlineAvailability=true&active=true&details.name=Advanced Graphics Rendering Technique*)",
        #     "subject": f'!TimerTrigger_Nvidia_Laptop - Best Buy Deals ({datetime.now()})',
        #     "columns":None,
        #     "detail_names":["Advanced Graphics Rendering Technique(s)", "GPU Video Memory (RAM)", "Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
        #     "offers":[]
        # },
        "television": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate in(Televisions,Digital_Signage_Displays_and_Players,Portable_TVs_and_Video)&screenSizeClassIn>39&salePrice<200&details.value!=Full HD&onSale=true&orderable=Available&onlineAvailability=true&active=true)",
            "subject": f'HttpTrigger1_Television - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Built-In Speakers", "Resolution", "Display Type", "Screen Size Class", "Screen Size", "Curved Screen"],
            "offers":[]
        }
    }
    # macbook and nvidia pcs deals
    for query in queries.keys():
        async_call(
            url=queries[query]["url"]
            , subject=queries[query]["subject"]
            , columns=queries[query]["columns"]
            , detail_names=queries[query]["detail_names"]
            , offers=queries[query]["offers"]
            , email=True
        )
    
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
