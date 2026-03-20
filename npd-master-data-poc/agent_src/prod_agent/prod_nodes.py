from .prod_state import ProdState
from .prod_util import (
    unit_conversion,
    plant_conversion
)

def start(state:ProdState): # Standby Node
    return state

def node_get_plant_code_name(state:ProdState):

    plant_dict = {}
    mdm = state['mdm_data']
    plant_sys_code = plant_conversion(mdm.get('initial_plant_name'))
    plant_dict['primary_plant'] = plant_sys_code

    return {"plant_location" : plant_dict}


def node_fg_forsale_std_unit(state:ProdState):
    mdm = state['mdm_data']['unit_measurement']

    stock_unit_code = unit_conversion(mdm.get('inner_container_um'))
    stock_unit_weight = mdm.get('inner_weight_max')

    sales_unit_code = unit_conversion(mdm.get('inner_container_um'))
    sales_unit_weight = mdm.get('inner_weight_max')

    pur_unit_code = unit_conversion(mdm.get('inner_container_um'))
    pur_unit_weight = mdm.get('inner_weight_max')


    return {
        'stock_unit_code': stock_unit_code,
        'stock_unit_weight': stock_unit_weight,
        'sales_unit_code': sales_unit_code,
        'sales_unit_weight': sales_unit_weight,
        'pur_unit_code': pur_unit_code,
        'pur_unit_weight': pur_unit_weight
    }
   

def node_fg_forsale_weight_unit(state:ProdState): #production see in KG regardless of product packaging

    stock_unit_code = unit_conversion("KG")
    stock_unit_weight = 1

    sales_unit_code = unit_conversion("KG")
    sales_unit_weight = 1
    
    pur_unit_code = unit_conversion("KG")
    pur_unit_weight = 1 

    return {
        'stock_unit_code': stock_unit_code,
        'stock_unit_weight': stock_unit_weight,
        'sales_unit_code': sales_unit_code,
        'sales_unit_weight': sales_unit_weight,
        'pur_unit_code': pur_unit_code,
        'pur_unit_weight': pur_unit_weight
        }

def node_fg_for_processing_unit(state:ProdState): #production (factory variations allow) -> sales(sell to affiliated processing factory)
    pass 

def node_nonfg_unit(state:ProdState): #productio view only
    pass

def node_get_process_type(state:ProdState):
    mdm = state['mdm_data']
    pass

def node_get_vat_flag(state:ProdState):
    pass


