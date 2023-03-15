import os
import datetime
import logging
import asyncio

from dateutil import tz
from datetime import datetime, timedelta

import azure.functions as func

from TimerTrigger1.api_bestbuy_async_discount_alert import bb_main

def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('ACTION!'.center(20, "*"))
    # utc_timestamp = datetime.datetime.utcnow().replace(
    #     tzinfo=datetime.timezone.utc).isoformat()

    # name = req.params.get('name')
    # if not name:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         name = req_body.get('name')

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('US/Pacific')

    utc = datetime.utcnow() - timedelta(minutes=361) # * utc time 361 minutes (6hrs and 1 min) before
    utc_timestamp = utc.replace(tzinfo=from_zone) # * explicitly apply utc timezone
    local = utc_timestamp.astimezone(to_zone) # * convert to local time

    LAST_UPDATE_DATE = local.strftime('%Y-%m-%dT%H:%M:%S') # * apply string format to date timestamp
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    df = loop.run_until_complete(bb_main(last_update_date=LAST_UPDATE_DATE))
    
    name = 'Stranger'
    
    if name:
        return func.HttpResponse(f"Hello {name}!\n\n{df}", mimetype="text/html")
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400
        )


'''
resources: 
https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
'''