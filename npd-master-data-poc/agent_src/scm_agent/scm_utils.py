#Layer 1 functions (load resources, build context for prompts)

import yaml
import os
from typing import Dict, Any


def load_reference_data(filename:str):

    filepath = os.path.join('agent_config','scm_config', filename)

    try: 
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            print(f'{filename} loaded') #Checkpoints
        return data
    
    except Exception as e:
        print(e)
        return None
    

def get_reference():
    return {
        'ref_temperature_zone':load_reference_data('temp_zone.yaml'),
        'ref_product_risk': load_reference_data('product_risk.yaml')
    }

def build_tempzone_context(reference_data): 

    context_line = []

    ref = reference_data['ref_temperature_zone']

    for zone, value in ref.items():
        line = f" - {zone}: {value.get('temp_range', 'N/A')}"
        context_line.append(line)

    result = "\n".join(context_line)

    return result


def build_productrisk_context(reference_data):
    context_line = []
    ref = reference_data['ref_product_risk']['risk_categories']

    for cat, value in ref.items():

        description = value['description']
        example = ",".join(value['examples'])
        tolerance =value['temp_tolerance']

        line = f" -{cat}: {description} with temperature tolarance of {tolerance} included product type: {example}"
        context_line.append(line)

    result = "\n".join(context_line)
    return result



    
