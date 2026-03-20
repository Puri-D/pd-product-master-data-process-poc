#Layer 2 functions (build propts, invoke llms)

from .scm_state import SCMState
from .scm_utils import (
    get_reference,
    build_tempzone_context,
    build_productrisk_context
)
import requests


def llm_parse_response(raw_response:str):
    pass

def llm_generate_temperature_control(state:SCMState): 

    mdm = state['mdm_data'] #basic data dict

    product_name = mdm.get('product_name', 'Error')
    pg1 = mdm.get('pg1', 'NA')
    pg2 = mdm.get('pg2', 'NA')
    pg6 = mdm.get('pg6', 'NA')
    storage = mdm.get('storage_type', 'FROZEN')
    shelf_life = mdm.get('shelf_life_days', 90)

    tempzone_context = build_tempzone_context(get_reference())
    productrisk_context = build_productrisk_context(get_reference())

    prompt = f"""You are an SCM cold chain expert. Determine precise temperature control requirements.

PRODUCT INFORMATION:
- Name: {product_name}
- Species: {pg6}
- Form: {pg1} (raw/marinated/cooked)
- Cut Type: {pg2}
- Storage Type: {storage}
- Shelf Life: {shelf_life} days

AVAILABLE TEMPERATURE ZONES (reference):
{tempzone_context}

RISK CATEGORIES (reference):
{productrisk_context}

Based on food safety standards and SCM best practices, determine these related fields:

1. TEMP_RANGE: Precise storage temperature with tolerance
   - Match product to appropriate zone from above
   - Consider species sensitivity:
     * Seafood: Strict (±1°C)
     * Poultry: Standard (±2°C)
     * Red meat: Standard (±2°C)
     * Vegetables: Flexible (±3°C)
   - Ice cream needs -23°C
   - Most frozen proteins: -18°C
   - Some vegetables: -12°C acceptable

2. CRITICAL_POINT: Maximum safe temperature threshold
   - Usually 2-3°C above target temperature
   - Include time limit (e.g., "for more than 30 minutes")
   - Stricter for high-risk products (raw poultry, seafood)
   - Format: "Never exceed [TEMP]°C for more than [TIME] minutes"

IMPORTANT:
- All fields must align with the product's risk level 

Respond in this dict type format (no extra text, no explanations):
    "temp_range": "[your answer]",
    "critical_point": "[your answer]",
    "risk_category": "[your answer]",
    "reasoning": "[brief reasoning for your decisions]"
"""
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
        dict_result = eval(result['response']) #convert string dict to actual dict

        return dict_result

    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise


