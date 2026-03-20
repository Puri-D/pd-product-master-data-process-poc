from langgraph.graph import StateGraph, END
from .prod_state import ProdState
from .prod_nodes import (
    start,
    node_get_plant_code_name,
    node_fg_forsale_std_unit,
    node_fg_forsale_weight_unit,
)

def agent_routing_isweight(state:ProdState): # Is the product sold by weight or standardized weight?
    mdm = state['mdm_data']
    is_weight = mdm.get('is_weighted', None)

    if is_weight is True:
        return "node_fg_forsale_weight_unit"
    else:
        return "node_fg_forsale_std_unit"
    


def build_prod_fg_forsale_workflow(): #standard products sold to retail sector
    
    workflow = StateGraph(ProdState)

    workflow.add_node("initialize", start)
    workflow.add_node("node_get_plant_code_name", node_get_plant_code_name)
    workflow.add_node("node_fg_forsale_std_unit", node_fg_forsale_std_unit)
    workflow.add_node("node_fg_forsale_weight_unit", node_fg_forsale_weight_unit)

    #_____________________Make workflow_________________________

    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "node_get_plant_code_name")
    workflow.add_conditional_edges("node_get_plant_code_name", agent_routing_isweight)
    workflow.add_edge("node_fg_forsale_std_unit", END)
    workflow.add_edge("node_fg_forsale_weight_unit", END)

    return workflow.compile()




def build_prod_wip_workflow():
    pass #nned to figure out how to store org level master

