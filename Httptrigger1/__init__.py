import os
import datetime
import logging
import asyncio

from typing import Tuple, Dict
from dateutil import tz
from datetime import datetime, timedelta

import azure.functions as func

from Httptrigger1.api_bestbuy_async_discount_alert import bb_main
from Httptrigger1.api_bestbuy_async_macbook_alert import bb_main as macbook_main
from Httptrigger1.api_bestbuy_async_nvidia_pc_alert import bb_main_nvidia

def async_call(url: str, subject: str, email: bool=False)  -> Tuple[str, Tuple]:
    """Makes an asynchronous call to a given URL.

    :param url: The URL to call.
    :type url: str
    :param subject: The subject of the email notification.
    :type subject: str
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
    df_html, df_shape = loop.run_until_complete(bb_main(url=url, subject=subject, email=email))
    df_html = df_html.replace('http', '<a href="http')
    df_html = df_html.replace('/pdp', '/pdp" target="_blank">urlLink</a>')
    df_html = df_html.replace('/cart', '/cart" target="_blank">addToCartUrl</a>')

    return df_html, df_shape


def main(req: func.HttpRequest) -> func.HttpResponse:

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
        "discounts": {
            "url":f"https://api.bestbuy.com/v1/products(priceUpdateDate>{LAST_UPDATE_DATE}&onSale=true&active=true&percentSavings>50&salePrice<>60696.99)",
            "subject": f'HttpTrigger1_Discounts - Best Buy Deals ({datetime.now()})'
        },
        "macbooks": {
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=macbook*&details.value!=intel*&orderable=Available&onlineAvailability=true&onSale=true&active=true)",
            "subject": f'HttpTrigger1_Macbooks - Best Buy Deals ({datetime.now()})'
        },
        "laptop": { # details.name=Advanced Graphics Rendering Technique*
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*)",
            "subject": f'HttpTrigger1_Nvidia_Laptops - Best Buy Deals ({datetime.now()})'
        },
        "desktop": {
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=desktop*&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*)",
            "subject": f'HttpTrigger1_Nvidia_Desktops - Best Buy Deals ({datetime.now()})'
        }
    }

    http_response: str = f"Hello {name}!</br>"

    # macbook and nvidia pcs deals
    for query in queries.keys():
        html, shape = async_call(url=queries[query]["url"], subject=queries[query]["subject"], email=False)
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
