import os
import smtplib
import asyncio
import aiohttp
import pandas as pd

import logging
import logging.handlers

from random import uniform
from datetime import datetime
from dateutil import tz
from time import perf_counter, sleep
from email.message import EmailMessage

import _config_bestbuy as _config_bestbuy

# formatting for logger
FILENAME = 'feller_buncher.log'
FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
DATEFORMAT = '%m/%d/%Y %I:%M:%S %p'
formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFORMAT)

# change default settings for name and logging level
logging.captureWarnings(True)
logging.getLogger().setLevel(logging.DEBUG)
# logging.basicConfig(encoding='utf-8', format=FORMAT, datefmt=DATEFORMAT, level=logging.DEBUG) # add version 3.9

# create handler 
ch = logging.StreamHandler() # show logs in terminal
mh = logging.handlers.SMTPHandler(
        mailhost=(_config_bestbuy.email_host, _config_bestbuy.email_port), 
        fromaddr=_config_bestbuy.email_sender, 
        toaddrs=_config_bestbuy.email_distribution, 
        subject='SMTP E-Mail NVIDIA PC Logs', 
        credentials=(_config_bestbuy.email_user, _config_bestbuy.email_password), 
        secure=()
    )

# set logging level (debug, info, warning, error, critical)
ch.setLevel(logging.DEBUG)
mh.setLevel(logging.ERROR)

# format handler00
ch.setFormatter(formatter)
mh.setFormatter(formatter)

# create logger with name and set logging level
lumberjack = logging.getLogger(__name__ + "- timertrigger1_nvidia_pc - bestbuy deals")
lumberjack.setLevel(logging.DEBUG)
lumberjack.addHandler(mh)


class Products:
    
    def __init__(self, datum):
        self.products = {}
        __collection = []
        __columns = ["sku", "name", "salePrice", "url", "addToCartUrl"]
        __names = ["GPU Brand", "GPU Video Memory (RAM)", "Graphics", "Processor Model", "Processor Model Number", "System Memory (RAM)", "Solid State Drive Capacity"]
        
        for column in __columns:
            for data in datum:
                __collection.append(data[column])
            
            self.products[column] = __collection
            __collection = []

        for name in __names:
            for data in datum:
                __next_value = False

                for detail in data['details']:
                    if name.lower() == detail['name'].lower():
                        __collection.append(detail['value'])
                        __next_value = True
                        break

                if __next_value:
                    continue

                else:
                    __collection.append(None)
            
            self.products[name] = __collection        
            __collection = []


def to_matrix(x, n):
    l = []
    for i in range(x):
        l.append(i+1)

    return [l[i:i+n] for i in range(0, len(l), n)]


async def ceiling_division(n, d):
    return -(n // -d)


def email_config():
    
    # * email configurations
    host = _config_bestbuy.email_host
    port = _config_bestbuy.email_port
    distribution = _config_bestbuy.email_distribution
    email_user = _config_bestbuy.email_user
    sender = _config_bestbuy.email_sender
    password = _config_bestbuy.email_password

    return host, port, distribution, email_user, sender, password


def send_email(subject, body):

    host, port, distribution, email_user, sender, password = email_config() # * email configurations
    
    # * email message content
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = distribution
    msg.set_content(body, subtype='html')

    # * create secure connection to email server, login and send email, then close connection
    with smtplib.SMTP_SSL(host, port) as smtp_server:
        smtp_server.login(email_user, password)
        smtp_server.send_message(msg)


def error_msg(e):
    # * send email when complete

    # * email subject and body
    subject = f'TimerTrigger1_NVIDIA_PC - Best Buy Products Error ({datetime.now()})'
    body = f'''\
error: {e}
Notification Sent (UTC): {datetime.now()}
by {email_config()[2]}
'''

    send_email(subject=subject, body=body)


def status_msg(df_total, df_disc, last_update_date):
    # * send email when complete, unable to send to cell phone if body is more than 2 lines
    
    df_nvidiapc = df_disc.reset_index(drop=True).to_html()
    df_nvidiapc = df_nvidiapc.replace('http', '<a href="http')
    df_nvidiapc = df_nvidiapc.replace('/pdp', '/pdp" target="_blank">urlLink</a>')
    df_nvidiapc = df_nvidiapc.replace('/cart', '/cart" target="_blank">addToCartUrl</a>')

    # * email subject and body
    subject = f'TimerTrigger1_Macbook - Best Buy Deals ({datetime.now()})'
    body = f'''<html><head></head><body>
<p>New deals since: {last_update_date}</p><br/>
<p>total shape: {df_total.shape}</p></br>
<p>disc. shape: {df_disc.shape}</p></br>
{df_nvidiapc}
</body></html>
'''

    send_email(subject=subject, body=body)


# * best buy api connections
async def api_bestbuy(init, session, url, batch_size, page_size, page, pages=0, total=0):
    # * configurations
    t0 = perf_counter()
    batch_size = max(1, batch_size)
    
    req_params = {
        'apiKey': _config_bestbuy.bestbuy_api_key, 
        'pageSize': page_size, 
        'page': page, 
        'format': 'json', 
        'show': 'sku,name,salePrice,url,addToCartUrl,details',
        'sort': 'priceUpdateDate.asc'
        }

    lumberjack.info(f'{url=} | {req_params["page"]=}')

    # * loop until response is 200
    while True:
        delay = round(uniform(0, (await ceiling_division(batch_size, 5)*.4*batch_size)), 1)
        await asyncio.sleep(delay)
        t1 = perf_counter()
        status_counter = 0

        async with session.get(url, params=req_params) as r:
            t2 = perf_counter()

            if t2-t1 < 1: sleep(1.1-(t2-t1)) # if request is less than 1 sec, wait until 1 sec is reached
            lumberjack.info(f'request: {page=} | {pages=} | {total=} | {t1=:.04f} | {delay=:.04f} | {r.status=}')
            
            if r.status != 200:
                # * send another request if call failed 
                if status_counter <= 4:
                    status_counter += 1
                    lumberjack.info(f'{status_counter=}')
                    continue

                else:
                    break

            data = await r.json(content_type=None) # content_type='text/html'
            
            if init == 1:
                return data
            # lumberjack.info(f'{data=}')

            break # exit loop
    
    # * if db is True and length of products table not 0, insert into database
    if len(data["products"]):

        # * create dataframes from collected data
        try:
            apple = Products(data['products'])
            df = pd.DataFrame(apple.products).reset_index(drop=True)
            
        except KeyError as e:
            lumberjack.error(f'{e=}', exc_info=True)
        
        except Exception as e:
            lumberjack.error(f'{e=}', exc_info=True)
            error_msg(e)

    t3 = perf_counter()
    lumberjack.info(f'dataframe: {df.shape=} | {(t2-t1)=:.04f} | {(t3-t2)=:.04f} | {(t3-t1)=:.04f} | {(t3-t0)=:.04f}')

    return df


def filter(df):
    df_filter = df.loc[:, :].reset_index(drop=True)
    df_filter = df_filter.sort_values(by=["salePrice", "name"], ascending=[True, True]).reset_index(drop=True)

    return df_filter


async def bb_main_nvidia(last_update_date=_config_bestbuy.last_update_date, page_size=100, batch_size=4, test=False):
    # * main entrypoint for app
    t0 = perf_counter()
    lumberjack.info(f'beg'.center(69, '*'))

    # * best buy api configurations
    # last_update_date = '2023-03-10T12:00:00'
    # url = f"https://api.bestbuy.com/v1/products(onSale=true&active=true&class in(GAMING LAPTOPS,SURFACE LAPTOP,MOBILE COMPUTING,SO LAPTOPS)&(search=nvidia))"
    url = f"https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&active=true&onSale=true&details.value=nvidia)"

    # * async connection to best buy api
    conn = aiohttp.TCPConnector(limit=4) # default 100, windows limit 64
    async with aiohttp.ClientSession(connector=conn) as session:
        response = await api_bestbuy(init=1, session=session, url=url, batch_size=batch_size, page_size=page_size, page=1)
        pages = response.get('totalPages', 0)
        total = response.get('total', 0)
        lumberjack.info(f'{last_update_date=} | {total=} | {pages=}')
        
        # * to gather data from all tasks
        data_concat = {}

        if pages > 0:
            batches = to_matrix(pages, batch_size)
            lumberjack.info('%s batches', len(batches))

            for _, batch in enumerate(batches):
                # session, url, key, last_update_date, page_size=100, batch_size=4, pages=1, page=1, total=0
                tasks = (api_bestbuy(init=0, session=session, url=url, batch_size=batch_size, page_size=page_size, page=page, pages=pages, total=total) for _, page in enumerate(batch))
                t4 = perf_counter()
                data = pd.concat(await asyncio.gather(*tasks), ignore_index=True).reset_index(drop=True)
                t5 = perf_counter()
                lumberjack.info(f'{batch=} | {t5-t4=:.04f} | {t5-t0=:.04f}')

                if t5-t4 < 1:
                    await asyncio.sleep(1)

                data_concat[_] = data

            df_total = pd.concat(data_concat, ignore_index=True).reset_index(drop=True)
            df_disc = filter(df_total)
        
        else:
            # * create empty dataframe
            df_total = pd.DataFrame()
            df_disc = pd.DataFrame()
            

    t_end = perf_counter()

    if df_disc.shape[0] > 0:
        
        # * if test is true export dataframe, otherwise update environment variable and send email
        if test:
            df_disc.to_excel('C:\\Users\\User\\downloads\\export.xlsx')
        
        else:
            # * send email notification
            status_msg(df_disc=df_disc, df_total=df_total, last_update_date=last_update_date)
        
        trigger_response = df_disc.reset_index(drop=True).to_html()

    else:
        # * create empty dataframe
        df_disc = pd.DataFrame()
        trigger_response = df_total.reset_index(drop=True).to_html()

    lumberjack.info(f'fin: {pages=} | {total=} | {df_disc.shape=} | {df_total.shape=} | {t_end-t0=:.06f}'.center(90, "*"))
    return trigger_response
    

if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(bb_main_nvidia(page_size=100, batch_size=4, test=False))
    except KeyboardInterrupt as ke:
        pass

    # clear and shutdown logger
    logging.getLogger('').handlers.clear
    logging.shutdown()
"""
https://api.bestbuy.com/v1/products?apiKey={}&pageSize=100&format=json&show=all&page=1

resources:
https://docs.aiohttp.org/en/stable/http_request_lifecycle.html
https://docs.aiohttp.org/en/stable/client_reference.html#tcpconnector

notes: update at approx. 10:49pm shows last update at 12:00am. data potentially 2 hours ahead.
"""
