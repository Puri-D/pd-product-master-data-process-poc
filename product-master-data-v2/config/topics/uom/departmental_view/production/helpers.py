from typing import List, Dict


def process_reference_data(reference_loader_result:Dict) -> Dict:
     
    unit_mapping = reference_loader_result.get('unit_mapping', {})

    return {
        'unit_mapping' : unit_mapping, 
    }


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.upper() in ['TRUE', '1', 'YES', 'T']
    return False


def apply_production_view(transformation_input:Dict, processed_reference:Dict):

    mdm_data = transformation_input['mdm']
    unit_mapping = processed_reference['unit_mapping']
    result = {}


    if to_bool(mdm_data.get('is_weighted', False)): 
        mdm_code = "KG"

    else:
        if to_bool(mdm_data.get('has_master', False)):
            mdm_code = mdm_data.get('master_container_um')
        else: 
            mdm_code = mdm_data.get('inner_container_um')

            
    if mdm_code in unit_mapping:
        detail = unit_mapping[mdm_code] # i.e. CS
        result['production_batch_unit'] = detail['production_unit']
        result['production_uom_code'] = detail['production_code']

    else: 
        result['production_batch_unit'] = "NA"
        result['production_uom_code'] = "NA"
        

    return result
