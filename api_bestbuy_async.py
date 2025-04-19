import aiohttp
import asyncio
import logging
import logging.handlers
import pandas as pd
import smtplib

from datetime import datetime
from email.message import EmailMessage
from random import uniform
from time import perf_counter

import _config_bestbuy as config

# Set up logging
def setup_logging():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', '%m/%d/%Y %I:%M:%S %p')
    
    logger = logging.getLogger(__name__ + "- azure function - bestbuy deals")
    logger.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    
    mh = logging.handlers.SMTPHandler(
        mailhost=(config.email_host, config.email_port), 
        fromaddr=config.email_sender, 
        toaddrs=config.email_distribution, 
        subject='SMTP E-Mail Best Buy Deals Logs', 
        credentials=(config.email_user, config.email_password), 
        secure=()
    )
    mh.setLevel(logging.ERROR)
    mh.setFormatter(formatter)
    
    logger.addHandler(ch)
    logger.addHandler(mh)
    return logger

lumberjack = setup_logging()

class Products:
    DEFAULT_COLUMNS = ["sku", "name", "salePrice", "url", "addToCartUrl", ]
    DEFAULT_DETAILS = [
        "Color", "Product Name", "Product Height", "Product Width", "Product Depth", 
        "Product Weight", "Warranty - Labor", "Warranty - Parts", 
    ]
    DEFAULT_OFFERS = ["startDate", "endDate"]
    
    def __init__(self, products_data, columns=None, detail_names=None, offers=None):
        self.columns = columns or self.DEFAULT_COLUMNS
        self.detail_names = detail_names or self.DEFAULT_DETAILS
        self.offers = offers or self.DEFAULT_OFFERS
        self.products = self._process_products(products_data)
    
    def _process_products(self, products_data):
        result = {}
        
        # Process basic columns
        for column in self.columns:
            result[column] = [product[column] for product in products_data]
        
        # Process details
        for detail_name in self.detail_names:
            result[detail_name] = []
            for product in products_data:
                value = next((
                    detail['value'] for detail in product['details']
                    if detail['name'].lower() == detail_name.lower()
                ), None)
                result[detail_name].append(value)
        
        # Process offers
        for offer_type in self.offers:
            offer_key = f"offer.{offer_type}"
            result[offer_key] = [
                {i: offer[offer_type] for i, offer in enumerate(product['offers'])}
                for product in products_data
            ]
        
        return result

def send_email(subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config.email_sender
    msg['To'] = config.email_distribution
    msg.set_content(body, subtype='html')

    with smtplib.SMTP_SSL(config.email_host, config.email_port) as smtp_server:
        smtp_server.login(config.email_user, config.email_password)
        smtp_server.send_message(msg)

def format_email_body(df_total, last_update_date):
    df = df_total.reset_index(drop=True).to_html()
    df = df.replace('http', '<a href="http')
    df = df.replace('/pdp', '/pdp" target="_blank">urlLink</a>')
    df = df.replace('/cart', '/cart" target="_blank">addToCartUrl</a>')

    return f'''<html><head></head><body>
<p>New deals since: {last_update_date}</p><br/>
<p>total shape: {df_total.shape}</p></br>
{df}
</body></html>
'''

async def make_api_request(session, url, params):
    delay = round(uniform(0, 2), 1)  # Random delay between 0-2 seconds
    await asyncio.sleep(delay)
    
    async with session.get(url, params=params) as response:
        if response.status != 200:
            lumberjack.error(f"API request failed with status {response.status}")
            return None
        return await response.json(content_type=None)

def chunk_list(lst, n):
    """Split a list into n-sized chunks"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

async def fetch_products(session, url, page, api_key, page_size=100):
    params = {
        'apiKey': api_key,
        'pageSize': page_size,
        'page': page,
        'format': 'json',
        'show': 'all',
        'sort': 'salePrice.asc'
    }
    return await make_api_request(session, url, params)

async def bb_main(url, subject, columns=None, detail_names=None, offers=None, 
                 last_update_date=config.last_update_date, page_size=100, 
                 batch_size=4, test=False, email=False):
    """Main entry point for Best Buy API interaction"""
    t0 = perf_counter()
    lumberjack.info('Starting Best Buy API fetch')

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=4)) as session:
        # Get total pages
        initial_response = await fetch_products(session, url, 1, config.bestbuy_api_key, page_size)
        if not initial_response:
            return "", (0, 0)
            
        total_pages = initial_response.get('totalPages', 0)
        total_items = initial_response.get('total', 0)
        
        if total_pages == 0:
            return pd.DataFrame().to_html(), (0, 0)

        # Fetch all pages in batches
        all_data = []
        page_numbers = range(1, total_pages + 1)
        batches = chunk_list(list(page_numbers), batch_size)

        for batch in batches:
            tasks = [
                fetch_products(session, url, page, config.bestbuy_api_key, page_size)
                for page in batch
            ]
            batch_results = await asyncio.gather(*tasks)
            
            for result in batch_results:
                if result and 'products' in result:
                    try:
                        products = Products(result['products'], columns, detail_names, offers)
                        df = pd.DataFrame(products.products)
                        all_data.append(df)
                    except Exception as e:
                        lumberjack.error(f"Error processing products: {e}", exc_info=True)

        if not all_data:
            return pd.DataFrame().to_html(), (0, 0)

        df_total = pd.concat(all_data, ignore_index=True)
        df_total = df_total.sort_values(by=["salePrice", "name"], ascending=[True, True])

        if test:
            df_total.to_excel(f'D:/temp/{subject.split(" ")[0]}.xlsx')
        
        if email:
            body = format_email_body(df_total, last_update_date)
            send_email(subject=subject, body=body)

        t_end = perf_counter()
        lumberjack.info(f'Completed in {t_end-t0:.2f}s. Found {len(df_total)} products')
        
        return df_total.to_html(), df_total.shape

if __name__ == '__main__':
    QUERIES = {
        "macbook": {
            "url": "https://api.bestbuy.com/v1/products(categoryPath.name=macbook*&salePrice<1000&details.value!=intel*&orderable=Available&onlineAvailability=true&onSale=true&active=true)",
            "subject": f'MacBook Deals ({datetime.now()})',
            "detail_names": ["Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
        },
        "nvidia": {
            "url": "https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&salePrice<1000&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*)",
            "subject": f'NVIDIA Laptop Deals ({datetime.now()})',
            "detail_names": ["Advanced Graphics Rendering Technique(s)", "GPU Video Memory (RAM)", "Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
        }
    }
    
    try:
        for query_name, query in QUERIES.items():
            asyncio.run(bb_main(
                url=query["url"],
                subject=query["subject"],
                detail_names=query["detail_names"],
                page_size=10,
                batch_size=4,
                test=True,
                email=False
            ))
    except KeyboardInterrupt:
        pass
    finally:
        logging.shutdown()

"""
https://api.bestbuy.com/v1/products?apiKey={}&pageSize=100&format=json&show=all&page=1

resources:
https://docs.aiohttp.org/en/stable/http_request_lifecycle.html
https://docs.aiohttp.org/en/stable/client_reference.html#tcpconnector

notes: update at approx. 10:49pm shows last update at 12:00am. data potentially 2 hours ahead.
"""
