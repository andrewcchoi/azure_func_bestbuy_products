import os
import uuid
import json
import asyncio
import aiohttp
import requests
import pandas as pd

from sqlalchemy import create_engine
from random import uniform
from time import perf_counter, sleep
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from azure.cosmos import exceptions, CosmosClient, PartitionKey

import config_bestbuy


def to_matrix(x, n):
    l = []
    for i in range(x):
        l.append(i+1)
    return [l[i:i+n] for i in range(0, len(l), n)]


def ceiling_division(n, d):
    return -(n // -d)


async def insert_db(r, engine, db_cols, container, cursor_mark):

    cols = ['nextCursorMark', 'total', 'totalPages', 'queryTime', 'totalTime', 'canonicalUrl', 
            'sku', 'name', 'type', 'startDate', 'new', 'activeUpdateDate', 'active', 'regularPrice', 
            'salePrice', 'clearance', 'onSale', 'categoryPath', 'customerReviewCount', 'customerReviewAverage', 
            'priceUpdateDate', 'itemUpdateDate', 'class', 'classId', 'subclass', 'subclassId', 'department', 'departmentId', 
            'theatricalReleaseDate', 'studio', 'manufacturer', 'modelNumber', 'condition', 'artistName', 'images', 'image', 'color']
    bool_cols = ["new", "active", "clearance", "onSale"]
    int_cols = ["total", "totalPages"]
    float_cols = ["queryTime", "totalTime", "regularPrice", "salePrice", "customerReviewCount", "customerReviewAverage", 'theatricalReleaseDate']
    date_cols = ["startDate", "activeUpdateDate", "priceUpdateDate", "itemUpdateDate"]
    
    with engine.connect() as cnx:
        io = r.json()
        # for product in io['products']:
        #     product['cursorMark'] = cursor_mark
        #     product['id'] = str(uuid.uuid4())
        #     container.create_item(body=product)
        
        df_meta = pd.DataFrame(io)
        df_meta = df_meta.iloc[:, :-1]
        df_products = pd.DataFrame(io['products'])
        df = df_meta.merge(df_products, how='inner', left_index=True, right_index=True)
        df = df.loc[:, cols]
        df.insert(0, 'request_timestamp', datetime.utcnow())

        for col in df.columns.tolist():
            if col in bool_cols:
                df.loc[:, col] = df.loc[:, col].astype('bool')
            elif col in int_cols:
                df.loc[:, col] = df.loc[:, col].astype('int64')
            elif col in float_cols:
                df.loc[:, col] = df.loc[:, col].astype('float64')
            elif col in date_cols:
                df.loc[:, col] = pd.to_datetime(df.loc[:, col], errors='coerce', infer_datetime_format=True)
            else:
                df.loc[:, col] = df.loc[:, col].astype('str')
                
        df.to_sql(name='products', con=cnx, if_exists='append', index=False)


async def main(api_index=0, folder_index=0, page_size=100, batch_size=5):

    t0 = perf_counter()
    # folderpath, datename, engine, db_cols, last_update_date, container = await initialize(folder_index=api_index)
    
    folders = ['products', 'categories', 'stores', 'products_update']
    datename = datetime.utcnow().strftime('%Y%m%d')
    cosmos_endpoint = config_bestbuy.bestbuy_cosmosdb_end_point
    cosmos_primary_key = config_bestbuy.bestbuy_cosmosdb_primary_key
    client = CosmosClient(cosmos_endpoint, cosmos_primary_key)
    db_name = 'BestBuyDB'
    database = client.create_database_if_not_exists(id=db_name)
    container_name = 'Products'
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path='/department'),
        offer_throughput=400
    )
    """"""
    # path = config_bestbuy.path
    path = config_bestbuy.path_test
    foldername = f'best_buy_{datename}\\{folders[folder_index]}'
    folderpath = os.path.join(path, foldername)

    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    """"""
    # db = os.path.join(config_bestbuy.path, 'bestbuy.db')
    # conn_string = f'sqlite:///{db}'
    # engine = create_engine(conn_string)

    # # params = quote_plus(config_bestbuy.bestbuy_sql_odbc_string)
    # # engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    # with engine.connect() as cnx:
    #     try:
    #         sel_stmt = "SELECT * FROM products LIMIT 0"
    #         df_db = pd.read_sql(sql=sel_stmt, con=cnx)
    #         db_cols = df_db.columns.tolist()

    #         last_update_stmt = 'SELECT MAX(itemUpdateDate) FROM products'
    #         df_itemUpdateDate = pd.read_sql(sql=last_update_stmt, con=cnx)
    #         last_update_date = df_itemUpdateDate.iloc[0, 0]
            
    #     except Exception as e:
    #         db_cols = []
    #         last_update_date = None
    

    async def api_bestbuy(page=1):
        chunk_size = 1024 # 64 * 2**10
        key = config_bestbuy.bestbuy_api_key
        apis = ['products', 'categories', 'stores'] #, f'products(itemUpdateDate>{last_update_date}&active=*)']
        url = f"https://api.bestbuy.com/v1/{apis[api_index]}"
        params = {
            'apiKey': key, 
            'pageSize': page_size, 
            'format': 'json', 
            'show': 'all',
            'page': page
            }

        delay = page/2
        # delay = 0
        # await asyncio.sleep(delay)
        t1 = perf_counter()

        conn = aiohttp.TCPConnector(limit=10) # default 100, windows limit 64
        async with aiohttp.ClientSession(connector=conn) as session:
            await asyncio.sleep(uniform(0,5)+uniform(.25,.75))
            while True:
                t3 = perf_counter()
                async with session.get(url, params=params) as r:
                    if r.status != 200:
                        print(f'{page=} | {t3=} | {r.status=}')
                        await asyncio.sleep(uniform(0,2))
                        continue
                    else:
                        data = await r.json(content_type=None) # content_type='text/html'
                        pg = data.get('currentPage', 0)
                        filename = f'best_buy_{datename}_{pg:05}.json'
                        filepath = os.path.join(folderpath, filename)

                        # with open(filepath, 'wb') as fd:
                        #     # data = json.dumps(await r.json(), indent=4)
                        #     async for chunk in r.content.iter_chunked(chunk_size):
                        #         fd.write(chunk)

                        with open(filepath, 'w') as f:
                            json.dump(data, f, indent=4)
                        break
            # insert_db(r=r, engine=engine, db_cols=db_cols, container=container, cursor_mark=nextcursorMark)
        
        t2 = perf_counter()
        print(f'{pg=}', f'{page=}', f'{t3=}', f'{(t2-t1)=}', f'{(t2-t0)=}', sep=' | ')
        return data

    
    data = await api_bestbuy()
    # print(pages)
    pages = data.get('totalPages', 0)

    batches = to_matrix(pages, batch_size)
    for batch in batches:
        tasks = (api_bestbuy(page=page) for page in batch)
        t4 = perf_counter()
        await asyncio.gather(*tasks)
        t5 = perf_counter()
        print(f'{batch=} | {t5-t4=}')
        if t5-t4 < 1:
            await asyncio.sleep(1)
    
    
    # batches = await to_matrix(pages, 5)
    # tasks = [
    #     api_bestbuy(page=1), api_bestbuy(page=2), api_bestbuy(page=3), api_bestbuy(page=4), api_bestbuy(page=5),
    #     api_bestbuy(page=6), api_bestbuy(page=7), api_bestbuy(page=8), api_bestbuy(page=9), api_bestbuy(page=10)
    # ]
    # r = await api_bestbuy(page=pg, api_index=api_index, page_size=page_size, last_update_date=last_update_date)
        
    
    print(f'fin: {perf_counter()-t0=}')
    # return await asyncio.gather(*tasks)
    

if __name__ == '__main__':
    # [0: 'products', 1: 'categories', 2: 'stores', 3: f'products(itemUpdateDate>{last_update_date}&active=*)']
    # await main(api_index=0, folder_index=0, page_size=100)
    # asyncio.run(main(api_index=0, folder_index=0, page_size=100))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(api_index=0, folder_index=0, page_size=100, batch_size=10))
    # loop.close()
