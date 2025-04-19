import asyncio
import logging as fellerbuncher
import azure.functions as func

from datetime import datetime, timedelta, timezone
from dateutil import tz

from api_bestbuy_async import bb_main
from .config import get_queries

def main(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger for Best Buy product search"""
    fellerbuncher.info('ACTION!'.center(20, "*"))
    
    # Get name from request
    name = req.params.get('name', 'stranger')
    
    # Get Pacific time
    utc = datetime.now(timezone.utc) - timedelta(minutes=361)
    local = utc.astimezone(tz.gettz('US/Pacific'))
    LAST_UPDATE_DATE = local.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Get queries and fetch results
    queries = get_queries(LAST_UPDATE_DATE)
    loop = asyncio.new_event_loop()
    results = []
    
    try:
        for query_name, params in queries.items():
            html, shape = loop.run_until_complete(
                bb_main(**params)
            )
            
            # Add HTML links
            html = (html.replace('http', '<a href="http')
                    .replace('/pdp', '/pdp" target="_blank">urlLink</a>')
                    .replace('/cart', '/cart" target="_blank">addToCartUrl</a>'))
            
            results.append(f"{query_name} {shape}:</br>{html}</br>")
            
        return func.HttpResponse(
            f"Hello {name}!</br>{''.join(results)}", 
            mimetype="text/html"
        )
    
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
    finally:
        loop.close()
