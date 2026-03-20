from .basic_state import BasicState
from .plant_parse import PlantLoad
from .shelflife_parse import get_shelf_life
from .llm_um_parse import LLMPackageParser
from .llm_attribute_hardfilter import Hardfilter
from .llm_attribute_embedd import (EmbeddingSearch, EmbeddingStorage)
from .llm_attribute_reranking import LLMReranking
import os
import pandas as pd
import json


def start(state:BasicState):

    raw = state['raw_data']
    return {
        'product_name': raw['product_name'],
        'material_desc_local':raw['product_name'],
        'material_desc_eng': raw['product_name'],
        'storage': raw['temp'],
        'tmp_business_group': raw['business_unit'],
        'tmp_product_type': raw['product_type'],
    }

def node_is_newvariation(state:BasicState):
    return {'is_new_variation': True}

def node_get_basic_plant(state:BasicState):

    raw = state['raw_data']
    unstruc_plant_detail = raw['plant_detail']
    plant_parser = PlantLoad()
    plant_parser.load_mas_plant_data

    if unstruc_plant_detail.strip() == "":
        return None

    else: 
        try: 
            plant_parser.load_mas_plant_data()

            match_group = plant_parser.get_plant_group(unstruc_plant_detail)
            match_province = plant_parser.get_province(unstruc_plant_detail)
            match_district = plant_parser.get_district(unstruc_plant_detail)
            match_result = plant_parser.fuzzy_match_loc(unstruc_plant_detail, match_group, match_district, match_province)

            top_result = plant_parser.get_plant_code_name(match_result)

            return {
                'initial_plant_code': top_result['code'],
                'initial_plant_name': top_result['name'],
                'initial_plant_score': top_result['score'],
                'tmp_business_group': match_group
                }
            
        except Exception as e:
            return {
                'initial_plant_code': e,
                'initial_plant_name': e,
                'initial_plant_score': e,
                'tmp_business_group': e
                }


def node_get_basic_shelflife(state:BasicState):
    
    raw = state['raw_data']

    unstruc_shelf_detail = raw['shelf_life']

    parser = get_shelf_life()

    parse_text = parser.shelf_life_parser(unstruc_shelf_detail)

    value = parse_text[0]
    unit = parse_text[1]
    day = parser.convert_to_day(parse_text)

    return {
        'shelf_life_value':value,
        'shelf_life_unit':unit,
        'shelf_life_day': day[0]
    }


def node_get_basic_unit_measurements(state:BasicState):
    
    parser = LLMPackageParser()
    raw = state['raw_data']
    unstruc_packing_text = raw['packing_detail']

    try:
        result = parser._llm_parser(unstruc_packing_text)
        result = json.loads(result)
        
        dict = {
            'size_dimension': unstruc_packing_text,
            'unit_measurement': result
        }

        if dict['unit_measurement']['inner_weight_max'] != dict['unit_measurement']['inner_weight_max']:
            dict['is_weighted'] = True

        else:
            dict['is_weighted'] = False

        print(dict)
        return dict

    except Exception as e:
        print(e)



def node_productgroup_get_top_similarity(state:BasicState):

    raw = state['raw_data']
    basic_bu = raw['business_unit']
    basic_prod_type = raw['product_type']
    basic_name = raw['product_name']
    sample_path = os.path.join('data','mas', 'mas_product.csv')
    filter = Hardfilter(sample_path)
    embed_storage_path = os.path.join('data','cache', 'poc_embeddings.pkl')
    

    try:
        #Load Embeddings resources
        EmbeddingStorage(storage_path = embed_storage_path)
        embed = EmbeddingSearch(storage_path=embed_storage_path)
        mas_product_df = pd.read_csv(sample_path)
        embed.embed_all_products(mas_product_df, text_column = 'material_name_local', force_recompute = False)

        #filtering products
        filter_sample = filter.filter_sample_pool(basic_bu, basic_prod_type)

        #embed search
        embedded_sample = embed.embed_search(
            basic_name,
            filter_sample,
            top_n = 5
            ) 
        return {'tmp_embedded_samples': embedded_sample}
    
    except Exception as e:
        return {'tmp_embedded_samples': e}
    



def node_productgroup_get_attributes(state:BasicState):

    #Populate prompt variables with state values
    product_name  = state['product_name']
    plant_group   = state['tmp_business_group']
    inner_container_um    = state['unit_measurement'].get('inner_container_um', '')
    master_container_um   = state['unit_measurement'].get('master_container_um', '')
    storage       = state['storage']
    product_type  = state['tmp_product_type'] 

    #make NPD's context for building prompt
    npd_info = {
        'product_name': product_name,
        'plant_group': plant_group,
        'inner_container_um': inner_container_um,
        'master_container_um': master_container_um,
        'storage': storage,
        'product_type': product_type,
    }

    embedded_samples = state['tmp_embedded_samples']
    
    #Call Function
    llm_attribute = LLMReranking()

    try: 
        print('passed')
        result_attributes = llm_attribute.classify(npd_info, embedded_samples)

        scores_attributes = {
            'pg1_score' : llm_attribute._pg_confidence_score("pg1",
                                                             result_attributes['final_classification']['pg1']['value'],
                                                             result_attributes['final_classification']['pg1']['source'],
                                                             npd_data=state,
                                                             sim_score=result_attributes['similarity']),
            'pg2_score' : llm_attribute._pg_confidence_score("pg1",
                                                             result_attributes['final_classification']['pg2']['value'],
                                                             result_attributes['final_classification']['pg2']['source'],
                                                             npd_data=state,
                                                             sim_score=result_attributes['similarity']),
            'pg3_score' : llm_attribute._pg_confidence_score("pg1",
                                                             result_attributes['final_classification']['pg3']['value'],
                                                             result_attributes['final_classification']['pg3']['source'],
                                                             npd_data=state,
                                                             sim_score=result_attributes['similarity']),
            'pg4_score' : llm_attribute._pg_confidence_score("pg1",
                                                             result_attributes['final_classification']['pg4']['value'],
                                                             result_attributes['final_classification']['pg4']['source'],
                                                             npd_data=state,
                                                             sim_score=result_attributes['similarity']),
            'pg5_score' : llm_attribute._pg_confidence_score("pg1",
                                                             result_attributes['final_classification']['pg5']['value'],
                                                             result_attributes['final_classification']['pg5']['source'],
                                                             npd_data=state,
                                                             sim_score=result_attributes['similarity']),
            'pg6_score' : llm_attribute._pg_confidence_score("pg1",
                                                             result_attributes['final_classification']['pg6']['value'],
                                                             result_attributes['final_classification']['pg6']['source'],
                                                             npd_data=state,
                                                             sim_score=result_attributes['similarity']),                                                             
        }

        return {
            'tmp_product_groups': result_attributes,
            'tmp_product_groups_score': scores_attributes,
            'is_new_variation': False,
            'pg1': result_attributes['final_classification']['pg1']['value'],
            'pg2': result_attributes['final_classification']['pg2']['value'],
            'pg3': result_attributes['final_classification']['pg3']['value'],
            'pg4': result_attributes['final_classification']['pg4']['value'],
            'pg5': result_attributes['final_classification']['pg5']['value'],
            'pg6': result_attributes['final_classification']['pg6']['value'],
        }

    except Exception as e:
        return e
    
    


