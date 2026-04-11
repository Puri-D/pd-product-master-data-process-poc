# config/topics/uom/departmental_view/sales/helpers.py

from typing import Dict

def process_reference_data(reference_loader_result: Dict) -> Dict:
    """Process reference data from loader."""
    
    sales_mapping = reference_loader_result.get('sales_mapping', {})
    
    return {
        'sales_mapping': sales_mapping
    }


def apply_sales_view(transformation_input: Dict, processed_reference: Dict) -> Dict:
    """Transform Production data to Sales View format."""
    
    # Extract data
    mdm_data = transformation_input['mdm']
    production_data = transformation_input['production']
    sales_mapping = processed_reference['sales_mapping']
    
    # Get production batch unit
    production_unit = production_data.get('production_batch_unit', 'NA')
    
    # Lookup in sales mapping
    if production_unit and production_unit in sales_mapping:
        sales_details = sales_mapping[production_unit]
        result = {
            'purchase_order_unit': sales_details['purchase_order_unit'],
            'purchase_order_code': sales_details['purchase_order_code']
        }
    else:
        # Fallback if production unit not mapped
        result = {
            'purchase_order_unit': 'NA',
            'purchase_order_code': 'NA'
        }
    
    return result