from .sales_state import SalesState
from .sales_util import (
    unit_conversion,
    build_pos_name_prompt
)
import requests

def start(state:SalesState): # Standby Node
    return state

def llm_pos_name(state:SalesState):
    mdm = state['mdm_data']
    prompt = build_pos_name_prompt(mdm)

    try: 
        response = requests.post(
            f"http://localhost:11434/api/generate",
            json={
                "model":"llama3.1:8b",
                "prompt":prompt,
                "stream": False,
                "temperature":0.05,
                "format": "json",
                "repeat_penalty": 1.0,
            }
        )

        result = response.json()
        output = eval(result['response'])
        print(output)

        return {
            'product_pos_name_en': output['pos_name_en'],
            'product_pos_name_th':output['pos_name_th']
        }
    
    except Exception as e:
        print(e)
        return {
            'product_pos_name_en': "NA",
            'product_pos_name_th': "NA"
        }


def get_shelf_life_day(state:SalesState): # Simple node to get shelf life data from basic data
    mdm = state['mdm_data']
    shelf_life_day = mdm.get('shelf_life_day', None)
    return {"shelf_life_day": shelf_life_day}

def get_tax_tag(state:SalesState): 
    mdm = state['mdm_data']
    pg6 = mdm.get('pg6', '').lower()
    if 'slaugther' in pg6: 
        return {"tax_type": "nonvat"}
    else: 
        return {"tax_type": "vat"}

def node_fg_std_unit(state:SalesState): #Standard FG products
    
    mdm = state['mdm_data']['unit_measurement']
    result = {}

    if mdm.get('has_master') == True:

        #Classify
        result['classification'] = "Standard FG, has master"

        #UM
        result['pack_um'] = unit_conversion(mdm.get('inner_container_um'))
        result.update(dict.fromkeys(['sales_um', 'pur_um', 'picking_um'], unit_conversion(mdm.get('master_container_um')))) 

        #Calculation Method
        result.update(dict.fromkeys(['sales_cal',  'pur_cal', 'picking_cal'],"M"))
        
        #Equivalent
        result['pack_equi'] = mdm.get('inner_weight_max')
        result.update(dict.fromkeys(['sales_equi', 'pur_equi',  'picking_equi'],mdm.get('inner_per_master_qty')))

        #Equivalent Unit
        result.update(dict.fromkeys(['sales_equi_um', 'pur_equi_um',  'picking_equi_um'],unit_conversion(mdm.get('inner_container_um'))))
        result['pack_equi_um'] = unit_conversion("KG")

    else:
        #Classify
        result['classification'] = "Standard FG, inner only"
        
        #UM
        result['pack_um'] = unit_conversion(mdm.get('inner_container_um'))
        result.update(dict.fromkeys(['sales_um', 'pur_um', 'picking_um'], unit_conversion(mdm.get('inner_container_um')))) 
        
        #Calculation Method
        result.update(dict.fromkeys(['sales_cal',  'pur_cal', 'picking_cal'],"M"))
        
        #Equivalent
        result['pack_equi'] = mdm.get('inner_weight_max')
        result.update(dict.fromkeys(['sales_equi', 'pur_equi',  'picking_equi'],1))
        
        #Equivalent Unit
        result.update(dict.fromkeys(['sales_equi_um', 'pur_equi_um',  'picking_equi_um'],unit_conversion(mdm.get('inner_container_um'))))
        result['pack_equi_um'] = unit_conversion("KG")


    return {'sales_unit_measurement': result}

    
def node_fg_weight_unit(state:SalesState): #Weighted FG products

    mdm = state['mdm_data']['unit_measurement']

    result = {}

    #Check if item_qty is EA (Whole Animal)

    if mdm.get('item_um') == 'EA': #Whole animal products
        
        #Classify
        result['classification'] = "weight whole FG"

        #UM
        result.update(dict.fromkeys(['pack_um','sales_um', 'pur_um', 'picking_um'],unit_conversion(mdm.get('item_um'))))
        

        #Calculation Method
        result.update(dict.fromkeys(['sales_cal',  'pur_cal', 'picking_cal'],"M"))
        
        #Equivalent
        result['pack_equi'] = mdm.get('item_weight_max')
        result.update(dict.fromkeys(['sales_equi', 'pur_equi', 'picking_equi'],1))

        #Equivalent Unit
        result.update(dict.fromkeys(['sales_equi_um', 'pur_equi_um',  'picking_equi_um'],unit_conversion(mdm.get('item_um'))))

    else: # Weigthed products

        #Classify
        result['classification'] = "weight FG (ex. raw meat)"

        #UM
        result.update(dict.fromkeys(['pack_um','sales_um', 'pur_um'],unit_conversion("KG")))
        result['picking_um'] = unit_conversion(mdm.get('inner_container_um')) if unit_conversion(mdm.get('inner_container_um')) else unit_conversion(mdm.get('item_um'))
        
        #Calculation Method
        result.update(dict.fromkeys(['sales_cal',  'pur_cal', 'picking_cal'],"M"))
        
        #Equivalent
        result.update(dict.fromkeys(['pack_equi', 'sales_equi', 'pur_equi'],1))
        result['picking_equi'] = mdm.get('inner_weight_max') if unit_conversion(mdm.get('inner_container_um')) else mdm.get('item_weight_max')

        #Equivalent Unit
        result.update(dict.fromkeys(['pack_equi_um', 'sales_equi_um', 'pur_equi_um',  'picking_equi_um'],unit_conversion("KG")))

    return {'sales_unit_measurement': result}



if __name__ == '__main__':
    data = {
         'product_name': 'Grilled Chicken Breast Teriyaki Flavor 200g',
         'material_desc_eng': 'Grilled Chicken Breast Teriyaki Flavor 200g',
         'material_desc_local': 'อกไก่ย่างรสเทอริยากิ 200 กรัม',
         'brand':'GoldenFresh',
         'pg4':'PAC',
         'pg5': 'FROZEN',
         'pg6': 'CHICKEN FURTHER',
     }
 
    state = {'mdm_data': data}
    result = llm_pos_name(state)
    print(result)
 





    

    


