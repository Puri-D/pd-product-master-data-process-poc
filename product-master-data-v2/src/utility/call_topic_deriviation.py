import importlib
from typing import Dict

def call_topic_derivation(topic_config: Dict, extracted_data: Dict) -> Dict: #Universal call of derivation generation from respective helpers topic

    topic_file = topic_config['topic']['file'] 
    helpers_path = f'config.topics.{topic_file}.helpers' 
    
    try:
        helpers = importlib.import_module(helpers_path)
        
        if hasattr(helpers, 'derive_fields'):
            return helpers.derive_fields(extracted_data) #call method derive_fields() in helpers function
        else:
            print(f"{helpers_path} has no derive_fields() function, check respective topic's helpers file")
            return {}
            
    except ImportError as e:
        print(f"Could not import {helpers_path}: {e}")
        return {}