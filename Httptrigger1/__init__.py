import os
import datetime
import logging
import asyncio

from typing import Tuple, Dict, List
from dateutil import tz
from datetime import datetime, timedelta

import azure.functions as func

from api_bestbuy_async import bb_main

def async_call(
        url: str
        , subject: str
        , columns: List=None
        , detail_names: List=None
        , offers: List=None
        , email: bool=False)  -> Tuple[str, Tuple]:
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
    :return: A tuple of the modified dataframe and its shape.
    :rtype: tuple(str, tuple)

    .. code-block:: python

        # Example of using async_call function
        url = "https://api.bestbuy.com/v1/products(longDescription=iPhone*|sku=7619002)"
        subject = "Best Buy Deals"
        email = False
        df, df_shape = async_call(url, subject, email)
        print(df)
        print(df_shape)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    df_html, df_shape = loop.run_until_complete(
        bb_main(
            url=url
            , subject=subject
            , columns=columns
            , detail_names=detail_names
            , offers=offers
            , email=email
        )
    )
    df_html = df_html.replace('http', '<a href="http')
    df_html = df_html.replace('/pdp', '/pdp" target="_blank">urlLink</a>')
    df_html = df_html.replace('/cart', '/cart" target="_blank">addToCartUrl</a>')

    return df_html, df_shape


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Runs a Python HTTP trigger function.

    This function logs an action message, gets the name parameter from the request,
    gets the current date and time in UTC and US/Pacific zones, formats the date and time as a string,
    calls four URLs asynchronously using the async_call function, and returns an HTTP response with
    the name and the HTML content from the URLs.

    Args:
        req (func.HttpRequest): An HTTP request object.

    Returns:
        func.HttpResponse: An HTTP response object with the status code, mimetype, and body.

    Examples:
        >>> import azure.functions as func
        >>> req = func.HttpRequest(method='GET', url='http://localhost:7071/api/HttpTrigger1?name=MASTER')
        >>> res = main(req)
        >>> print(res.get_body())
        Hello MASTER!
        discounts (10,11):
        <table border="1" class="dataframe">
          <thead>
            <tr style="text-align: right;">
              <th></th>
              <th>name</th>
              <th>salePrice</th>
              <th>percentSavings</th>
              <th>urlLink</th>
              <th>addToCartUrl</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>0</th>
              <td>Apple - MacBook Pro - 13.3" Display with Touch Bar - Intel Core i5 - 8GB Memory - 256GB SSD - Space Gray</td>
              <td>999.99</td>
              <td>23.08</td>
              <td><a href="https://www.bestbuy.com/site/apple-macbook-pro-13-3-display-with-touch-bar-intel-core-i5-8gb-memory-256gb-ssd-space-gray/6287719.p?skuId=6287719" target="_blank">urlLink</a></td>
              <td><a href="https://api.bestbuy.com/click/-/6287719/cart" target="_blank">addToCartUrl</a></td>
            </tr>
            ...
          </tbody>
        </table>

        macbooks (10,11):
        ...
        
        laptop (10,11):
        ...

        desktop (10,11):
        ...
    """
    logging.info('ACTION!'.center(20, "*"))
    # utc_timestamp = datetime.datetime.utcnow().replace(
    #     tzinfo=datetime.timezone.utc).isoformat()

    name = req.params.get('name')
    logging.info(f'name: {name}')
    
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            name = 'Stranger'
            pass
        else:
            name = req_body.get('name')

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Pacific')

    utc = datetime.utcnow() - timedelta(minutes=361) # * utc time 361 minutes (6hrs and 1 min) before
    utc_timestamp = utc.replace(tzinfo=from_zone) # * explicitly apply utc timezone
    local = utc_timestamp.astimezone(to_zone) # * convert to local time

    LAST_UPDATE_DATE = local.strftime('%Y-%m-%dT%H:%M:%S') # * apply string format to date timestamp
    
    # Define a type alias for the inner dictionary
    inner_query = Dict[str, str]

    # dictionary with url queries and email subject
    queries: Dict[str, inner_query] = {
        "discount": {
            "url":f"https://api.bestbuy.com/v1/products(priceUpdateDate>{LAST_UPDATE_DATE}&onSale=true&active=true&percentSavings>50&salePrice<>60696.99)",
            "subject": f'TimerTrigger1_Discount>50% - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "url", "addToCartUrl", "priceUpdateDate"],
            "detail_names":[],
            "offers":None
        },
        "headphones": {
            "url":f"https://api.bestbuy.com/v1/products(productTemplate=Headphones_and_Headsets&class=HEADPHONES&subclassId=410&details.value=noise cancel*&orderable=Available&onlineAvailability=true&active=true&onSale=true)",
            "subject": f'HttpTrigger1_Headphones_Noise_Cancelling - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Headphone Fit", "Microphone Features", "Sound Isolating", "Built-In Microphone", "Noise Cancelling (Active)"],
            "offers":[]
        },
        "ps5 controller": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate=Gaming_Controllers&manufacturer=Sony&albumTitle=PlayStation 5*&details.value=PlayStation 5&orderable=Available&onlineAvailability=true&active=true&onSale=true)",
            "subject": f'TimerTrigger1_Playstation 5 Controller - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "color", "url", "addToCartUrl"],
            "detail_names":[],
            "offers":[]
        },
        "television": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate in(Televisions,Digital_Signage_Displays_and_Players,Portable_TVs_and_Video)&screenSizeClassIn>39&salePrice<200&details.value!=Full HD&onSale=true&orderable=Available&onlineAvailability=true&active=true)",
            "subject": f'HttpTrigger1_Television - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Built-In Speakers", "Resolution", "Display Type", "Screen Size Class", "Screen Size", "Curved Screen"],
            "offers":[]
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
        "desktop": {
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=desktop*&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*)",
            "subject": f'HttpTrigger1_Nvidia_Desktops - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Advanced Graphics Rendering Technique(s)", "GPU Video Memory (RAM)", "Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
            "offers":[]
        },
        "purple": {
            "url":f"https://api.bestbuy.com/v1/products(onSale=true&condition=new&active=true&(color=purple*|color=lilac*|color=lavender*|color=violet*|color=amethyst*|color=plum*))",
            "subject": f'TimerTrigger1_Purple - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "url", "addToCartUrl", "priceUpdateDate"],
            "detail_names":[],
            "offers":None
        },
    }

    http_response: str = f"Hello {name}!</br>"

    # macbook and nvidia pcs deals
    for query in queries.keys():
        html, shape = async_call(
            url=queries[query]["url"]
            , subject=queries[query]["subject"]
            , columns=queries[query]["columns"]
            , detail_names=queries[query]["detail_names"]
            , offers=queries[query]["offers"]
            , email=False
        )
        http_response += f"{query} {shape}:</br>{html}</br>"

    if name:
        return func.HttpResponse(http_response, mimetype="text/html")
    
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400
        )


'''
resources: 
https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
'''
