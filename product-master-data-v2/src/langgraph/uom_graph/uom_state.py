from typing import TypedDict

class UOMExtractionState(TypedDict):

    # Configuration
    topic_config: dict       # Complete YAML config
    
    # Input data
    source_data: dict        # {'packing_detail': '...'}
    
    # Later 1: MDM Extraction results
    extracted_data: dict     # LLM-extracted fields
    derived_data: dict       # Calculated fields

    # Layer 2 Departmental View
    production_view_data: dict
    sales_view_data: dict

    metadata: dict
    field_confidences: dict