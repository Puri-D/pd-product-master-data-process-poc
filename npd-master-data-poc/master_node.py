from agent_src.sales_agent.sales_workflow import build_sales_workflow
from agent_src.scm_agent.scm_workflow import build_scm_workflow
from agent_src.prod_agent.prod_workflow import build_prod_fg_forsale_workflow
from basic_parsers.basic_workflow import build_basic_workflow
from master_state import MasterState
from pprint import pprint


def flag_new_variation(state:MasterState): #Stop workflow and flag for human input if new variation detected in basic view (essential before AI agents)
    return { 
        'basic_complete': False,
        'basic_remark': "New variation - use manual product requisition *requires human input for basic classification",
        'sales_complete': False,
        'scm_complete': False,
        'sales_view': {},
        'scm_view': {}
    }

def run_basic_data_parser(state:MasterState): #Process raw_input into basic_view
    
    raw_data = state['raw_input']
    basic_app = build_basic_workflow()
    result = basic_app.invoke({
            'raw_data': raw_data
    })
    dict_result = result.to_dict() if hasattr(result, 'to_dict') else result
    del dict_result['raw_data']
    del dict_result['tmp_embedded_samples']
    return {'basic_view': dict_result, 'basic_complete': True}


def run_sales_agent(state:MasterState): #Process basic_view into sales_view

    sales_app = build_sales_workflow()
    print("Invoking sales agent")


    result = sales_app.invoke({
        "mdm_data": state['basic_view']
    })

    filtered_result = {
        'product_pos_name_en':result.get('product_pos_name_en'),
        'product_pos_name_th':result.get('product_pos_name_th'),
        'sales_unit_measurement': result.get('sales_unit_measurement', 'NA'),
        'shelf_life_day': result.get('shelf_life_day', 'NA'),
        'tax_type': result.get('tax_type', 'NA'),
    }

    return {'sales_view': filtered_result, 'sales_complete': True}

def run_scm_agent(state:MasterState): #Process basic_view into scm_view

    scm_app = build_scm_workflow()
    print("Invoking scm agent")

    result = scm_app.invoke({
        "mdm_data": state['basic_view']
    })

    del result['mdm_data']
    return {'scm_view': result, 'scm_complete': True}


def run_prod_agent(state:MasterState): #Process basic_view into production_view

    prod_app = build_prod_fg_forsale_workflow()
    print("Invoking production agent")

    result = prod_app.invoke({
        "mdm_data": state['basic_view']
    })

    del result['mdm_data']
    
    return {'prod_view': result, 'prod_complete': True}

