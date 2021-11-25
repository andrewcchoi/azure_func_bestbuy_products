# %%
import os
import json
import requests

from time import perf_counter, sleep
from datetime import datetime, timedelta

import config_bestbuy

# %%
def initialize(folder_index=0):

    folders = ['products', 'categories', 'stores', 'products_update']
    datename = datetime.utcnow().strftime('%Y%m%d')
    path = config_bestbuy.path
    foldername = f'best_buy_{datename}\\{folders[folder_index]}'
    folderpath = os.path.join(path, foldername)

    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    return folderpath, datename


def api_bestbuy(cursorMark="*", api_index=0, page_size=100):
    key = config_bestbuy.key_bestbuy
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    apis = ['products', 'categories', 'stores', f'products(itemUpdateDate>{yesterday}&active=*)']
    url = f"https://api.bestbuy.com/v1/{apis[api_index]}"
    payload = {
        'apiKey': key, 
        'pageSize': page_size, 
        'format': 'json', 
        'show': 'all',
        'cursorMark': cursorMark
        }
    r = requests.get(f'{url}', params=payload)

    return r


def main(api_index=0, page_size=100):

    folderpath, datename = initialize(folder_index=api_index)
    nextcursorMark = "*"
    pg = 0
    pages = api_bestbuy(cursorMark=nextcursorMark, api_index=api_index, page_size=page_size).json()['totalPages']
    print(f'{pages=}')
    sleep(1)
    t1 = perf_counter()

    while True:
        print(f'{pg=}', f'{nextcursorMark=}', f'{t1=}', f'{perf_counter()-t1=}', sep=' | ')

        r = api_bestbuy(cursorMark=nextcursorMark, api_index=api_index, page_size=page_size)

        if r.status_code == 200:
            try:
                if len(r.json()['products']) == 0:
                    print("fin")
                    break      

                nextcursorMark = r.json()['nextCursorMark']
                pg += 1
            
            except (NameError, ValueError, KeyError) as e:
                print(f'{e=}')
                t1 = perf_counter()

            else:
                pass

            finally:
                pass

            filename = f'best_buy_{datename}_{pg:05}.json'
            filepath = os.path.join(folderpath, filename)

            with open(filepath, 'w') as f:
                json.dump(r.json(), f, indent=4)
            print(f'saved to {filepath}')
        
        timer = perf_counter()-t1
        if (pg)%5==0:
            if timer<1:
                sleep(1-timer)
            t1 = perf_counter()
    


# %%
if __name__ == '__main__':

    # api_index = {0: 'products', 1: 'categories', 2: 'stores', 3: 'products(itemUpdateDate>today&active=*)'}
    main(api_index=3, page_size=100)


# %% [markdown]
# Tip: To query for updates or deltas since you last walked through the result set you can use the itemUpdateDate attribute. To ensure that your query results include changes to a product’s active/inactive status, add active=* to your query parameters. 
# For example: .../v1/products(itemUpdateDate>2017-02-06T16:00:00&active=*)?format=json&pageSize=100&cursorMark=*&apiKey=YOUR_API_KEY
# For example: .../v1/products(itemUpdateDate>today&active=*)?format=json&pageSize=100&cursorMark=*&apiKey=YOUR_API_KEY
# "https://api.bestbuy.com/v1/products(releaseDate>today)?format=json&show=sku,name,salePrice&apiKey=YourAPIKey"


