from typing import List, Dict

def extract_unit_codes(units_data: List[Dict]):
    """Extract unit codes."""
    return [unit['mdm_unit_code'] for unit in units_data]
#=========================================================================


def build_text_to_code_mapping(units_data: List[Dict]):
    """Build text→code mapping."""
    mapping = {}
    for unit in units_data:
        code = unit['mdm_unit_code']
        for lang, texts in unit['mdm_unit_text'].items():
            for text in texts:
                mapping[text.lower()] = code
    return mapping
#=========================================================================

def build_code_to_variations_mapping(units_data: List[Dict]):
    """Build code→variations mapping."""
    code_to_variations = {}
    for unit in units_data:
        code = unit['mdm_unit_code']
        variations = []
        for lang, texts in unit['mdm_unit_text'].items():
            variations.extend([t.lower() for t in texts])
        code_to_variations[code] = sorted(variations)
    return code_to_variations
#=========================================================================

def process_reference_data(reference_loader_result:Dict) -> Dict: #Flatter yaml dict

    """ get load data from topic's reference data 
    (use subitem in reference_data as key in dict)"""

    units = reference_loader_result.get('unit_translations', [])
    code_to_variations = build_code_to_variations_mapping(units)

    return {
        'code_to_variations': code_to_variations
    }

#=========================================================================


# Note: derive_fields is COVENTIONAL NAME FOR ALL TOPIC - IT PROCESS THE REMAINING DERIVATIVE FIELD AFTER LLM EXTRACTED DATA 
def derive_fields(extracted_data: Dict) -> Dict: 
    
    derived = {}

    # Master weight max
    if (extracted_data.get('inner_weight_max') is not None and 
        extracted_data.get('inner_per_master_qty') is not None):
        
        derived['master_weight_max'] = (
            extracted_data['inner_weight_max'] * 
            extracted_data['inner_per_master_qty']
        )

    else:
        derived['master_weight_max'] = None

    
    # Master weight min
    if (extracted_data.get('inner_weight_min') is not None and 
        extracted_data.get('inner_per_master_qty') is not None):
        derived['master_weight_min'] = (
            extracted_data['inner_weight_min'] * 
            extracted_data['inner_per_master_qty']
        )
    else:
        derived['master_weight_min'] = None


    # has_master
    if extracted_data['inner_per_master_qty'] is not None:
        derived['has_master'] = True
    else:
        derived['has_master'] = False


    # is Weigthed
    if extracted_data.get('inner_weight_min') != extracted_data.get('inner_weight_max'):
        derived['is_weighted'] = True
    else:
        derived['is_weighted'] = False

    #Default Value (it actually have other unit but in this case only KG applies)
    derived['base_um'] = "KG"


    return derived