from typing import TypedDict, List, Dict

class SalesState(TypedDict):
    # Input
    mdm_data: dict
    #type, is_weight, animal

    product_pos_name_en: str
    product_pos_name_local: str
    sales_unit_measurement: dict
    shelf_life_day:str
    tax_type: str



    
    