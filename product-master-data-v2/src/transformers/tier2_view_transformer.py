import importlib
from typing import Dict
from datetime import datetime
from src.utility.reference_loader import ReferenceDataLoader

class Tier2ViewTransformer:

    def __init__(self, view_config:Dict, parent_topic: str): # for importlib path

        self.view_config = view_config
        self.parent_config = parent_topic #Just name of mdm canonical file

        self.view_id = self.view_config['topic']['id']
        self.view_type = self.view_config['topic']['type']
        
        #for transform method
        self.view_file = self.view_config['topic']['file']

        #Pre load helpers
        self._load_helpers()

        self.reference_loader = ReferenceDataLoader(view_config)

    def _load_helpers(self):

        view_file = self.view_config['topic']['file']
        helpers_path = f"config.topics.{self.parent_config}.departmental_view.{view_file}.helpers"
        self.helpers = importlib.import_module(helpers_path)

    def transform(self, transformation_input:Dict) -> Dict:
        
        #Load reference data
        raw_reference = self.reference_loader.fetch_all()
        processed_reference = self.helpers.process_reference_data(raw_reference)

        #Dynamic Calling Apply 
        apply_func_name = f"apply_{self.view_file}_view"

        if not hasattr(self.helpers, apply_func_name): #Check if it has function in helpers
            raise AttributeError(f"Helpers module missing function: {apply_func_name}")

        apply_func = getattr(self.helpers, apply_func_name) #Look into f"config.topics.{self.parent_config}.departmental_view.{view_file}.helpers" and find function 
        data = apply_func(transformation_input, processed_reference) #Call Function 

        return {
            'data': data,
            f'{self.view_file}_view_metadata': {
                'view_id': self.view_config['topic']['id'],
                'parent_topic': self.view_config['topic']['source_topic'],
                'created_at': datetime.now().isoformat(),
            }
        }
    
