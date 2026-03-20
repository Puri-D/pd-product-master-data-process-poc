import yaml
import os
from typing import Dict, Any


def load_reference_data(filename:str):

    filepath = os.path.join('agent_config','prod_config', filename)

    try: 
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data
    
    except Exception as e:
        print(e)
        return None
    
def get_reference():
    return {
        'unit_mapping' : load_reference_data('unit_mapping_config.yaml'),
        'plant_mapping' : load_reference_data('plant_sap_to_sys_mapping.yaml')
    }

def unit_conversion(unit:str):
    um_mapping = get_reference()['unit_mapping']['um_sap_to_local']

    sap_unit_list = list(um_mapping.keys())

    if unit in sap_unit_list:
        return um_mapping.get(unit)
    else: 
        return f"No mapping for SAP Unit: {unit}"
    

def plant_conversion(name:str):
    um_mapping = get_reference()['plant_mapping']['plant_sap_to_sys_mapping']

    sap_plant_name = list(um_mapping.keys())
    if name in sap_plant_name:
        return um_mapping.get(name)
    else: 
        return f"No mapping for SAP Plant Name: {name}"
    
