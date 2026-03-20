from langgraph.graph import StateGraph, END
from .sales_state import SalesState
from .sales_nodes import (
    start,
    node_fg_std_unit,
    node_fg_weight_unit,
    get_shelf_life_day,
    get_tax_tag,
    llm_pos_name
)

def agent_routing_isweight(state:SalesState): # Is the product sold by weight or standardized weight?
    mdm = state['mdm_data']
    is_weight = mdm.get('is_weighted', None)

    if is_weight is True:
        return "node_fg_weight_unit"
    else:
        return "node_fg_std_unit"
    


def build_sales_workflow():

    workflow = StateGraph(SalesState)

    #Make nodes definitions
    workflow.add_node("initialize", start)
    workflow.add_node("get_shelflife_day", get_shelf_life_day)
    workflow.add_node("get_tax_tag", get_tax_tag)
    workflow.add_node("node_fg_std_unit", node_fg_std_unit)
    workflow.add_node("node_fg_weight_unit", node_fg_weight_unit)
    workflow.add_node("llm_pos_name", llm_pos_name)


    #_____________________Make workflow_________________________

    workflow.set_entry_point("initialize")

    #Conditional - Product Type
    workflow.add_conditional_edges("initialize", agent_routing_isweight)

    #Conditional - Unit of measurements
    workflow.add_edge("node_fg_std_unit", "get_shelflife_day")
    workflow.add_edge("node_fg_weight_unit", "get_shelflife_day")
    workflow.add_edge("get_shelflife_day", "get_tax_tag")
    workflow.add_edge("get_tax_tag", "llm_pos_name")
    workflow.add_edge("llm_pos_name", END)

    return workflow.compile()





