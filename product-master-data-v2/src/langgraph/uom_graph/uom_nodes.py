from .uom_state import UOMExtractionState
from .uom_utils import (
    get_tier3_extractor,
    get_llm_fields,
    get_derived_fields,
    call_view_transformation
)
import yaml, json
from datetime import datetime
from src.utility.call_topic_deriviation import call_topic_derivation
from src.utility.confidence_cal import (
    tier3_llmrag_calculate_confidence,
    tier2_derived_calculate_confidence
)

def extract_tier3_node(state: UOMExtractionState) -> UOMExtractionState:

    print("\n" + "*"*80)
    print("NODE: Tier 3 LLM Extraction")
    print("*"*80)
    
    # Get fields from config
    llm_fields = get_llm_fields(state['topic_config'])
    
    print(f"\nExtracting {len(llm_fields)} fields via LLM")
    
    if not llm_fields:
        print("No LLM fields configured")
        return state
    
    # CALL LLM: Get extractor
    extractor = get_tier3_extractor(state['topic_config']) 
    
    # Extract
    result = extractor.extract(
        field_names=llm_fields,
        source_data=state['source_data']
    )

    # =======================
    # Build Confidence Scoring
    # =======================

    rag_scores = []
    valid_uom_codes = ['BAG', 'CS', 'CASE', 'KG', 'G', 'PC', 'EA', 'PAC', 'SAC', 'TRA', 'TNK', 'STK'] #Not really ideal but Work around for now
    field_confidences = {}

    if hasattr(extractor, 'similarity_engine') and extractor.similarity_engine:
        # Get the last similarity search results
        if hasattr(extractor.similarity_engine, '_last_similarities'):
            rag_scores = extractor.similarity_engine._last_similarities

    for field_name, field_value in result.items():
        # Determine value library for this field
        if field_name.endswith('_um') or field_name.endswith('_unit'):
            value_lib = valid_uom_codes
        else:
            value_lib = None
        
        # Calculate confidence
        confidence = tier3_llmrag_calculate_confidence(
            extracted_value=field_value,
            rag_similarity_score=rag_scores if rag_scores else None,
            value_lib=value_lib
        )
    
        field_confidences[field_name] = confidence

    print(f"\nConfidence Scores:")
    for field, conf in field_confidences.items():
        print(f"  {field}: {conf:.2f}")

    # =======================
    # Build LLM Metadata
    # =======================
    
    topic_config = state['topic_config']['topic']

    metadata = {
        'record_identity' : {
            'record_id': f"UOM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'topic':  topic_config['name'],
            'created_time': f"{datetime.now().isoformat()}",
            'record_version': 1,
        },
        'source' : {
            'source_system':topic_config['tier3_llm']['source_file'],
            'source_type':topic_config['tier3_llm']['source_type'],
            'source_field': topic_config['tier3_llm']['source_text_field'],
            'source_extraction_method': topic_config['tier3_llm']['source_extraction_method']
        },
        'extraction' : {
            'tier3_fields': llm_fields,
            'tier2_fields': [],
            'tier1_fields': [],    
            'extraction_method': 'tier3_llm_rag',
            'rag_enabled': True,
            'llm_model': topic_config['tier3_llm']['model'],
            'total_fields_extracted': len(result)
        }
    }

    output = {
        **state,
        'extracted_data': result,
        'metadata': metadata,
        'field_confidences': field_confidences
    }


    # Update state
    return output

def derive_fields_node(state: UOMExtractionState) -> UOMExtractionState:

    print("\n" + "*"*80)
    print("NODE: Derive Calculated Fields")
    print("="*80)
    
    # Get derived fields from config
    derived_fields = get_derived_fields(state['topic_config'])
    metadata = state.get('metadata', {}).copy()
    field_confidences = state.get('field_confidences', {}).copy()
    
    
    if not derived_fields:
        print("No derived fields configured")
        return state
    
    print(f"Calculating {len(derived_fields)} derived fields")
    
    # Call topic's derivation logic
    derived_data = call_topic_derivation(
        state['topic_config'],
        state['extracted_data']
    )

    confidence_input = {}

    for field, value in state['extracted_data'].items():
        confidence_input[field] = value
        confidence_input[f'_metadata_{field}_confidence'] = field_confidences.get(field, 1.0)
    
    for derived_field_name in derived_data.keys():
        field_config = state['topic_config']['fields'][derived_field_name]
        
        if 'extraction' in field_config and 'derived_config' in field_config['extraction']:
            depends_on = field_config['extraction']['derived_config']['depends_on']
        elif 'derived_config' in field_config:
            depends_on = field_config['derived_config']['depends_on']
        else:
            print(f"Warning: No derived_config found for {derived_field_name}")
            depends_on = []
        
        if depends_on:
            confidence = tier2_derived_calculate_confidence(
                field_name=derived_field_name,
                depends_on_fields=depends_on,
                extracted_data=confidence_input
            )
            field_confidences[derived_field_name] = confidence
        else:
            # No dependencies, default confidence
            field_confidences[derived_field_name] = 1.0
    
    print(f"\nDerived Field Confidences:")
    for field in derived_data.keys():
        print(f"  {field}: {field_confidences[field]:.2f}")
    
    print(f"Calculated {len(derived_data)} fields")


    # =========================================
    # Build MDM Metadata
    # =========================================

    field_dependencies = {}

    for derived_field_name in derived_data.keys():  # ← Loop through ACTUAL fields
        
        # Skip if not in config
        if derived_field_name not in state['topic_config']['fields']:
            continue
        
        field_config = state['topic_config']['fields'][derived_field_name]
        
        # Get depends_on (safe access)
        if 'extraction' in field_config and 'derived_config' in field_config['extraction']:
            depends_on = field_config['extraction']['derived_config']['depends_on']
        elif 'derived_config' in field_config:
            depends_on = field_config['derived_config']['depends_on']
        else:
            continue
        
        if depends_on:
            field_dependencies[derived_field_name] = {
                'depends_on': depends_on
            }

    metadata['lineage'] = {
        'field_dependencies': field_dependencies
    }

    metadata['human_review'] = {
            'review_status': 'pending',
            'review_by': '',
            'review_at': '',
            'correction_made':'False'
        }
    
    metadata['extraction']['tier2_fields'] =  derived_fields
    metadata['extraction']['total_fields'] = len(state['extracted_data']) + len(derived_data)

    output = {
        **state,
        'derived_data': derived_data,
        'extracted_data': {
            **state['extracted_data'], # Merge extracted + derived into extracted_data
            **derived_data
        },
        'metadata': metadata,
        'field_confidences': field_confidences
    }
    
    # Update state
    return output


def display_results_node(state: UOMExtractionState) -> UOMExtractionState:

    print("\n" + "="*80)
    print("NODE: Final Results")
    print("="*80)
    
    print("\nExtracted + Derived Data:")
    print("-" * 80)
    
    for field, value in state['extracted_data'].items():
        print(f"{field}: {value}")

    #Show Production View Data
    if 'production_view_data' in state and state['production_view_data']:
        print("\nProduction View Data:")
        print("-" * 80)
        prod_data = state['production_view_data'].get('data', {})
        for field, value in prod_data.items():
            print(f"{field}: {value}")
        
        print("\nProduction Metadata:")
        print("-" * 80)
        metadata = state['production_view_data'].get('metadata', {})
        for key, value in metadata.items():
            print(f"{key}: {value}")
    
    return state
    

# =========================================================================
# Production Department Node
# =========================================================================


def transform_production_node(state: UOMExtractionState):

    with open('config/topics/uom/departmental_view/production/view_def.yaml', encoding='utf-8') as f:
        production_config = yaml.safe_load(f)
        
    transformation_input = {'mdm': state['extracted_data']}

    result = call_view_transformation(view_config=production_config,
                                      transformation_input= transformation_input,
                                      parent_topic='uom')
    
    # =========================================
    # Build SPECIFIC Metadata
    # =========================================

    metadata = result.get('production_view_metadata', {}).copy()
    derived_fields = get_derived_fields(production_config)
    field_dependencies = {}
    
    for derived_field_name in derived_fields:
        print(derived_field_name)
        
        if derived_field_name in production_config['fields'].keys():
            field_dependencies[derived_field_name] = {
                'depends_on': production_config['fields'][derived_field_name]['extraction']['depends_on']}
        else:
            continue
    

    #Add extraction detail
    metadata['extraction'] = {
        "tier2_field": derived_fields,
        "extraction_method": "tier2",
        "total_field_extracted": len(derived_fields)
    }

    # Add lineage to metadata
    metadata['lineage'] = {
        'field_dependencies': field_dependencies
    }

    # Add Approval Detail
    metadata['human_review'] = {
            'review_status': 'pending',
            'review_by': '',
            'review_at': '',
            'correction': False
    }

    
    result['production_view_metadata'] = metadata
    
    return {**state, 'production_view_data': result}


# =========================================================================
# Sales Department Node
# =========================================================================

# At the end of the file, add:

def transform_sales_node(state: UOMExtractionState) -> UOMExtractionState:
    """Transform Production + MDM data to Sales View."""
    
    print("\n" + "*"*80)
    print("NODE: Sales View Transformation")
    print("*"*80)
    
    # Load sales view config
    import yaml
    with open('config/topics/uom/departmental_view/sales/view_def.yaml', encoding='utf-8') as f:
        sales_config = yaml.safe_load(f)
    
    # Build transformation input (Sales needs BOTH MDM and Production!)
    transformation_input = {
        'mdm': state['extracted_data'],
        'production': state['production_view_data']['data']  # ← Uses Production output!
    }
    
    # Transform
    result = call_view_transformation(
        view_config=sales_config,
        transformation_input=transformation_input,
        parent_topic='uom'
    )

    # =========================================
    # Build SPECIFIC Metadata
    # =========================================


    # Lineage
    metadata = result.get('sales_view_metadata', {}).copy()
    derived_fields = get_derived_fields(sales_config)
    field_dependencies = {}
    
    for derived_field_name in derived_fields:
        print(derived_field_name)
        
        if derived_field_name in sales_config['fields'].keys():
            field_dependencies[derived_field_name] = {
                'depends_on': sales_config['fields'][derived_field_name]['extraction']['depends_on']}
        else:
            continue
    
    #Extraction
    metadata['extraction'] = {
        "tier2_field": derived_fields,
        "extraction_method": "tier1",
        "total_field_extracted": len(derived_fields)
    }

    # Add lineage to metadata
    metadata['lineage'] = {
        'field_dependencies': field_dependencies
    }

    # Add Approval Detail
    metadata['human_review'] = {
            'review_status': 'pending',
            'review_by': '',
            'review_at': '',
            'correction': False
    }


    
    result['sales_view_metadata'] = metadata

    # Update state
    return {
        **state,
        'sales_view_data': result
    }