from typing import Dict, Any
from datetime import datetime

def get_queries(LAST_UPDATE_DATE: str) -> Dict[str, Dict[str, Any]]:
    """Returns query configurations for different product searches
    resources: 
    https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
"""
    return {
        "television": {
            "url":f"https://api.bestbuy.com/v1/products(productTemplate in(Televisions,Digital_Signage_Displays_and_Players,Portable_TVs_and_Video)&screenSizeClassIn>39&salePrice<200&details.value!=Full HD&onSale=true&orderable=Available&onlineAvailability=true&active=true&priceUpdateDate>{LAST_UPDATE_DATE})", 
            "subject": f'!TimerTrigger_Television - Best Buy Deals ({datetime.now()})', 
            "columns":None, 
            "detail_names":["Built-In Speakers", "Resolution", "Display Type", "Screen Size Class", "Screen Size", "Curved Screen"], 
            "offers":[], 
        },
        # "nvidia": {
        #     "url":f"https://api.bestbuy.com/v1/products(categoryPath.name=laptop*&salePrice<1000&orderable=Available&onlineAvailability=true&active=true&details.name=Advanced Graphics Rendering Technique*&priceUpdateDate>{LAST_UPDATE_DATE})",
        #     "subject": f'!TimerTrigger_Nvidia_Laptop - Best Buy Deals ({datetime.now()})',
        #     "columns":None,
        #     "detail_names":["Advanced Graphics Rendering Technique(s)", "GPU Video Memory (RAM)", "Graphics", "Processor Model", "System Memory (RAM)", "Solid State Drive Capacity"],
        #     "offers":[]
        # },
    }