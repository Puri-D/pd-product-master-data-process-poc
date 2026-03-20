from typing import TypedDict, List, Dict

class ProdState(TypedDict):

    #Input
    mdm_data: dict

    #Plant
    plant_location: dict #can be multiple plants for same product
    classification: str #description of what product is use for

    #Common fields
    process_type: str #FG/RM/WIP
    stock_unit_code: str
    stock_unit_weight: str

    #Sales (sell unit to retail sector)
    vat_flag: bool
    sales_unit_code: str
    sales_unit_weight: float #kg/unit 

    #Purchase (transfer unit to processing factory)
    purchase_group: str
    pur_unit_code: str
    pur_unit_weight: float #kg/unit

    

    #____________________Plant-specific fields__________________________
    
    #Purchasing (transfers to processing factory)
    
    location_specifics: Dict[str, dict]


    #{
    #   'MB2': {
    #     'pur_unit_code': str,      # ← Can differ
    #     'pur_unit_size': float,    # ← Can differ    
    #   }
    # }
    


    


