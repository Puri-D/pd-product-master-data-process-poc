import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any

class ReferenceDataLoader:

    """
    This function read into the reference_data sector in topic_config.yaml/ or view_config.yaml
    look into the path and load all of it into a sectorial python dict.
    """

    def __init__(self, topic_config: Dict):

        self.topic_config = topic_config #Load data topic into class
        self._reference_data = {}

        print(f'ReferenceDataLoader for "{topic_config['topic']['id']}" Initialized')


    def _load_file(self, file_path:str): # Load resources path from topic_def.yaml 

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Reference data not found: {path}\n"
                f"Original path: {file_path}"
            )
        
        if path.suffix in ['.yaml', '.yml']: # if resouce in yaml form
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            print(f"Loaded YAML with {len(data)} items")

        elif path.suffix in ['.csv']: #If resource in csv form
            data = pd.read_csv(path, encoding='utf-8')
            print(f"Loaded CSV with {len(data)} items")

        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        return data
    
    def fetch(self, ref_name:str): 

        """
        Get individual keys in reference_data that loaded.
        """

        # ===================================================
        # CASE 1: Check self._reference_data for used ref_name
        # ===================================================
        if ref_name in self._reference_data:
            print(f"Success: '{ref_name}' from cache")
            return self._reference_data[ref_name]

        # ===================================================
        # CASE 2: Not cached, need to load (CACHE MISS)
        # ===================================================

        ref_config = self.topic_config['topic']['reference_data'].get(ref_name)

        if ref_config is None:
            print(f"Failed: '{ref_name}' not found")
            return None
        
        # Extract path string from .yaml
        if isinstance(ref_config, str):
            file_path = ref_config # In case yaml has [reference_data][ref_name]: 'path/path'
        else:
            file_path = ref_config.get('path') # Most Common

        # Load from file_path
        try:
            print(f"  Loading '{ref_name}'...")
            data = self._load_file(file_path) #New Loads
            self._reference_data[ref_name] = data # Cache into self._reference_data for next time
            return data
            
        except Exception as e:
            print(f"Failed: {e}")
            return None
        

    def fetch_all(self):
        """
        Get all reference into dict in one go
        """
        data = {}
        all_references = self.topic_config['topic']['reference_data']
        for key in all_references:
            data[key] = self.fetch(key)
        return data

        





    
  