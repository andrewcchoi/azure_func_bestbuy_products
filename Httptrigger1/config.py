from typing import Dict, Any
from datetime import datetime

def get_queries(LAST_UPDATE_DATE: str) -> Dict[str, Dict[str, Any]]:
    """Returns query configurations for different product searches
    resources: 
    https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
"""
    return {
        "discount": {
            "url":f"https://api.bestbuy.com/v1/products(priceUpdateDate>{LAST_UPDATE_DATE}&onSale=true&active=true&percentSavings>50&salePrice<>60696.99)",
            "subject": f'HttpTrigger1_Discount>50% - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "url", "addToCartUrl", "priceUpdateDate"],
            "detail_names":[],
            "offers":None
        },
        "headphones": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate=Headphones_and_Headsets&class=HEADPHONES&subclassId=410&details.value=noise cancel*&orderable=Available&onlineAvailability=true&active=true&onSale=true)",
            "subject": f'HttpTrigger1_Headphones_Noise_Cancelling - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Headphone Fit", "Microphone Features", "Sound Isolating", "Built-In Microphone", "Noise Cancelling (Active)"],
            "offers":[]
        },
        "ps5 controller": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate=Gaming_Controllers&manufacturer=Sony&albumTitle=PlayStation 5*&details.value=PlayStation 5&orderable=Available&onlineAvailability=true&active=true&onSale=true)",
            "subject": f'HttpTrigger1_Playstation 5 Controller - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "color", "url", "addToCartUrl"],
            "detail_names":[],
            "offers":[]
        },
        "television": {
            "url":"https://api.bestbuy.com/v1/products(productTemplate in(Televisions,Digital_Signage_Displays_and_Players,Portable_TVs_and_Video)&screenSizeClassIn>84&salePrice<1000&details.value!=Full HD&onSale=true&orderable=Available&onlineAvailability=true&active=true)",
            "subject": f'HttpTrigger1_Television - Best Buy Deals ({datetime.now()})',
            "columns":None,
            "detail_names":["Built-In Speakers", "Resolution", "Display Type", "Screen Size Class", "Screen Size", "Curved Screen"],
            "offers":[]
        },
        "macbook": {
            "url":"https://api.bestbuy.com/v1/products(name=macbook pro*&categoryPath.name=macbook*&details.value!=intel&orderable=Available&onlineAvailability=true&onSale=true&active=true&preowned=false&subclassId=7835)",
            "subject": f'HttpTrigger1_Macbook - Best Buy Deals ({datetime.now()})',
            "columns":["sku", "name", "salePrice", "onSale", "url", "addToCartUrl"],
            "detail_names":["Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
            "offers":[]
        },
        "nvidia": {# details.name=Advanced Graphics Rendering Technique*
            "url":"https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&onSale=true&orderable=Available&onlineAvailability=true&active=true&details.value=nvidia&details.value!=1650*&details.value!=1660*)",
            "subject": f'HttpTrigger1_Nvidia_Pc - Best Buy Deals ({datetime.now()})',
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
            "url":"https://api.bestbuy.com/v1/products(onSale=true&condition=new&active=true&(color=purple*|color=lilac*|color=lavender*|color=violet*|color=amethyst*|color=plum*))",
            "subject": f'HttpTrigger1_Purple - Best Buy Deals ({datetime.now()})',
            "columns":["salePrice", "name", "url", "addToCartUrl", "priceUpdateDate"],
            "detail_names":[],
            "offers":None
        },
    }
