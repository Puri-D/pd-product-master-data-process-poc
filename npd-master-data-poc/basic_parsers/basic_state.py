from typing import TypedDict, List, Dict

class BasicState(TypedDict): #AKA basic view dict
    raw_data: dict

    #Material Category
    material_group:str
    material_type:str

    #basic data
    product_name:str
    material_desc_local:str
    material_desc_eng:str
    brand:str ### 
    spec_code:str ###
    storage:str 
    is_export: str ###

    size_dimension:str ###     
    unit_measurement: dict ###
    is_weigthed: bool

    initial_plant_code:str
    initial_plant_name:str

    shelf_life_value:int
    shelf_life_unit:str
    shelf_life_day:str


    pg1: str
    pg2: str
    pg3: str
    pg4: str
    pg5: str
    pg6: str


    
    #utlity fields
    is_new_variation: bool
    tmp_business_group:str #(chicken,swine,rte) temp data 
    tmp_product_type:str #chicken furrther/slaugther
    tmp_embedded_samples: dict
    tmp_product_groups: dict 
    tmp_product_groups_score: dict 
    tmp_newvariation: str


    

