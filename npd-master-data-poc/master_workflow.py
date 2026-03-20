from langgraph.graph import StateGraph, END
from master_state import MasterState
from master_node import (
    run_basic_data_parser,
    run_sales_agent,
    run_scm_agent,
    run_prod_agent,
    flag_new_variation
)

def routing_new_variation(state:MasterState):
    
    mdm = state['basic_view']

    if mdm['is_new_variation'] == True: #prompt user to manually input basic product group 1-6
        print("New variation detected - requires human input for basic classification")
        return "flag_new_variation"
    
    elif mdm['is_new_variation'] == False:
        print("Variation with suggested values - sending to sales and scm agent")
        return "prod_agent", "sales_agent", "scm_agent" #will change to routing product type


def routing_product_type(state:MasterState): # Check if product is Finished Goods (FG) or Raw Material (RM,WIP,etc.) and route accordingly
    mdm = state['basic_view']
    product_type = mdm.get('pg5', '').lower() #use basic data pg5 (FROZEN CHILL is consider fg other isnt)

    if product_type in ['frozen', 'chill']:
        # production -> sales -> scm
        pass
    else: 
        # production (business exception) -> end
        pass 


def build_master_workflow():

    workflow = StateGraph(MasterState)

    workflow.add_node(
        "flag_new_variation",
        flag_new_variation
    )

    workflow.add_node(
        "basic_data_parser",
        run_basic_data_parser
    )

    workflow.add_node(
        "sales_agent",
        run_sales_agent
    )

    workflow.add_node(
        "scm_agent",
        run_scm_agent
    )

    workflow.add_node(
        "prod_agent",
        run_prod_agent
    )
    #change later when link sales to scm
    workflow.set_entry_point("basic_data_parser")
    workflow.add_conditional_edges("basic_data_parser", routing_new_variation)
    workflow.add_edge("flag_new_variation", END)
    workflow.add_edge("sales_agent", END)
    workflow.add_edge("scm_agent", END)
    workflow.add_edge("prod_agent", END)

    app = workflow.compile()

    return app
