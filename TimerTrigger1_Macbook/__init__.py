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
    """Runs a Python timer trigger function.

    This function calls two URLs asynchronously using the async_call function,
    and sends emails with responses in html tables.

    Args:
        mytimer (func.TimerRequest): A timer request object.

    Raises:
        Exception: If any error occurs during the execution of the function.

    Examples:
        >>> import azure.functions as func
        >>> mytimer = func.TimerRequest()
        >>> main(mytimer)
        *******ACTION!*******
        Calling https://api.bestbuy.com/v1/products(categoryPath.name=macbook*&details.value!=intel*&orderable=Available&onlineAvailability=true&onSale=true&active=true) with subject HttpTrigger1_Macbook - Best Buy Deals (2023-09-02 23:02:01.123456)
        Sending email notification...
        Calling https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*) with subject HttpTrigger1_Nvidia_Pc - Best Buy Deals (2023-09-02 23:02:01.123456)
        Sending email notification...
        The timer is not past due.
        Python timer trigger function ran at 2023-09-01 23:02:01.123456+00:00
    """

    logging.info('ACTION!'.center(20, "*"))

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Pacific')

    utc = datetime.utcnow() - timedelta(minutes=1441) # * utc time 1_441 minutes (24hrs and 1 min) before
    utc_timestamp = utc.replace(tzinfo=from_zone) # * explicitly apply utc timezone
    local = utc_timestamp.astimezone(to_zone) # * convert to local time

    LAST_UPDATE_DATE = local.strftime('%Y-%m-%dT%H:%M:%S') # * apply string format to date timestamp

    # Define a type alias for the inner dictionary
    inner_queries = Dict[str, str]

    # Use the type alias for the outer dictionary
    queries: Dict[str, inner_queries] = {
        "purple": {
            "url":f"https://api.bestbuy.com/v1/products(onSale=true&conidtion=new&active=true&(color=purple*|color=lilac*|color=lavender*|color=violet*|color=amethyst*|color=plum*))",
            "subject": f'TimerTrigger1_Purple - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "url", "addToCartUrl", "priceUpdateDate"],
            "detail_names":[],
            "offers":None
        },
        "macbook": {
            "url":"https://api.bestbuy.com/v1/products(name=macbook pro*&categoryPath.name=macbook*&details.value!=intel&orderable=Available&onlineAvailability=true&onSale=true&active=true&preowned=false&subclassId=7835)",
            "subject": f'TimerTrigger1_Macbook - Best Buy Deals ({datetime.now()})',
            "columns":["sku", "name", "salePrice", "onSale", "url", "addToCartUrl"],
            "detail_names":["Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
            "offers":[]
        },
        "nvidia": {# details.name=Advanced Graphics Rendering Technique*
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*)",
            "subject": f'TimerTrigger1_Nvidia_Pc - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Advanced Graphics Rendering Technique(s)", "GPU Video Memory (RAM)", "Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
            "offers":[]
        },
        "television": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate in(Televisions,Digital_Signage_Displays_and_Players,Portable_TVs_and_Video)&screenSizeClassIn>39&salePrice<999&details.value!=Full HD&onSale=true&orderable=Available&onlineAvailability=true&active=true)",
            "subject": f'TimerTrigger1_Television - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Built-In Speakers", "Resolution", "Display Type", "Screen Size Class", "Screen Size", "Curved Screen"],
            "offers":[]
        },
        "ps5 controller": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate=Gaming_Controllers&manufacturer=Sony&albumTitle=PlayStation 5*&details.value=PlayStation 5&orderable=Available&onlineAvailability=true&active=true&onSale=true)",
            "subject": f'TimerTrigger1_Playstation 5 Controller - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "color", "url", "addToCartUrl"],
            "detail_names":[],
            "offers":[]
        },
        "headphones": {
            "url":f"https://api.bestbuy.com/v1/products(productTemplate=Headphones_and_Headsets&class=HEADPHONES&subclassId=410&details.value=noise cancel*&orderable=Available&onlineAvailability=true&active=true&onSale=true)",
            "subject": f'HttpTrigger1_Headphones_Noise_Cancelling - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Headphone Fit", "Microphone Features", "Sound Isolating", "Built-In Microphone", "Noise Cancelling (Active)"],
            "offers":[]
        },
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

'''
resources: 
https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
'''
