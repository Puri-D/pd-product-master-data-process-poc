import importlib
from typing import List, Dict
from src.extractors.tier3_llm_extractor import Tier3LLMExtractor



def get_tier3_extractor(topic_config: Dict) -> Tier3LLMExtractor: # Create the LLM extractor
    
    global _tier3_extractor
    _tier3_extractor = None

    if _tier3_extractor is None:
        print("Initializing Tier3LLMExtractor...")
        _tier3_extractor = Tier3LLMExtractor(topic_config)
        print("Extractor ready")

    return _tier3_extractor


def get_llm_fields(topic_config:Dict) ->List[str]: # Get topic yaml LLM fields into a list

    llm_fields = []
    
    for field_name, field_config in topic_config.get('fields', {}).items():
        extraction = field_config.get('extraction', {})
        
        # Skip derived and tier2 fields
        if extraction.get('primary_tier') in ['derived', 2]:
            continue
        
        # It's tier 3 - get output field name
        if extraction.get('primary_tier') == 3:
            output_field = extraction.get('output_field', field_name)
            llm_fields.append(output_field)
    
    return llm_fields


def get_derived_fields(topic_config: Dict) -> List[str]:
    
    derived_fields = []
    
    # Get all fields from config
    fields = topic_config.get('fields', {})
    
    # Loop through each field
    for field_name, config in fields.items():
        extraction = config.get('extraction', {})
        primary_tier = extraction.get('primary_tier')
        
        if primary_tier == 'derived':
            derived_fields.append(field_name)
    
    return derived_fields
# ========================================================
# View Generation
# ========================================================

def call_view_transformation(view_config:Dict, transformation_input:Dict, parent_topic:str): #Transformation includes all of the data from prior generations

    from src.transformers.tier2_view_transformer import Tier2ViewTransformer

    transformer = Tier2ViewTransformer(view_config=view_config,
                                       parent_topic=parent_topic)
    
    return transformer.transform(transformation_input)