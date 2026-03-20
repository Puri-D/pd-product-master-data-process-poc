import yaml
import os
import json


def load_reference_data(filename:str):

    filepath = os.path.join('agent_config','sales_config', filename)

    try: 
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            #print(f'{filename} loaded') #Checkpoints
        return data
    
    except Exception as e:
        print(e)
        return None
    
def get_reference():
    return {
        'sales_mapping' : load_reference_data('mapping_config.yaml'),
        'pos_name_config': load_reference_data('abbv.yaml')
    }

def unit_conversion(unit:str):
    um_mapping = get_reference()['sales_mapping']['um_sap_to_local']

    sap_unit_list = list(um_mapping.keys())

    if unit in sap_unit_list:
        return um_mapping.get(unit)
    else: 
        return f"No mapping for SAP Unit: {unit}"\
        
def build_pos_name_prompt(basic_data):

    config =  get_reference()['pos_name_config']

    rules = config.get('pos_name_limit')
    abbrev_en = config.get('abbv_en', {})
    abbrev_th = config.get('abbv_th', {})
    priority = config.get('compress_priority', {})

    char_limit_en = rules.get('char_limit_en', 24)
    char_limit_th = rules.get('char_limit_th', 20)

    desc_en = basic_data.get('material_desc_eng', '')
    desc_th = basic_data.get('material_desc_local', '')
    brand = basic_data.get('brand', '')
    pg4 = basic_data.get('pg4', '')
    pg5 = basic_data.get('pg5', '')
    pg6 = basic_data.get('pg6', '')

    prompt = f"""You are a product naming specialist for a Thai food manufacturing company.
Your task: generate SHORT POS register names from full product descriptions.
 
PRODUCT TO COMPRESS:
- Full name (EN): {desc_en}
- Full name (TH): {desc_th}
- Brand: {brand}
- Product group: {pg4} / {pg5} / {pg6}
 
CHARACTER LIMITS:
- English POS name: maximum {char_limit_en} characters (including spaces)
- Thai POS name: maximum {char_limit_th} characters (including spaces)
 
APPROVED ABBREVIATION DICTIONARY (English):
{json.dumps(abbrev_en, ensure_ascii=False, indent=2)}
 
APPROVED ABBREVIATION DICTIONARY (Thai):
{json.dumps(abbrev_th, ensure_ascii=False, indent=2)}
 
COMPRESSION RULES:
1. ALWAYS KEEP: {json.dumps(priority.get('always_keep', []))}
   - Core protein (chicken, duck, pork, fish) is NEVER abbreviated
   - The differentiator (flavor/variant) that distinguishes from siblings MUST remain
2. KEEP IF SPACE ALLOWS: {json.dumps(priority.get('keep_if_space', []))}
3. DROP FIRST: {json.dumps(priority.get('drop_first', []))}
   - Weight (200g, 1kg) can be dropped — barcode maps to SKU
   - Filler words (style, flavor, type) are dropped
4. DO NOT EXCEED THE CHARACTER LIMITS

   RESPOND IN EXACTLY THIS PYTHON DICT FORMAT (no other text):
{{
  "pos_name_en": "<english POS name within {char_limit_en} chars>",
  "pos_name_th": "<thai POS name within {char_limit_th} chars>",
  "reasoning": "<1 sentence explaining what was abbreviated/dropped and why>"
}}
   """
    return prompt





    
