from langgraph.graph import StateGraph, END
from .basic_state import BasicState
from .basic_node import (
    start,
    node_get_basic_plant,
    node_get_basic_shelflife,
    node_get_basic_unit_measurements,
    node_productgroup_get_top_similarity,
    node_productgroup_get_attributes,
    node_is_newvariation
)

def routing_new_variation(state:BasicState):
    
    #get top embedding sample similarity score
    score = state['tmp_embedded_samples'][0].get('similarity', 0)

    if score > 0.8:
        return 'node_productgroup_get_attributes'
    else:
        return 'node_is_newvariation'
    
def checkpoint(state:BasicState):
    return state
    

def build_basic_workflow():

    workflow = StateGraph(BasicState)

    workflow.add_node('start', start)
    workflow.add_node('checkpoint', checkpoint)
    workflow.add_node('node_get_basic_plant', node_get_basic_plant)
    workflow.add_node('node_get_basic_shelflife', node_get_basic_shelflife)
    workflow.add_node('node_get_basic_unit_measurements', node_get_basic_unit_measurements)
    workflow.add_node('node_productgroup_get_top_similarity', node_productgroup_get_top_similarity)
    workflow.add_node('node_productgroup_get_attributes', node_productgroup_get_attributes)
    workflow.add_node('node_is_newvariation', node_is_newvariation)


    #Make Workflow
    workflow.set_entry_point("start")

    workflow.add_edge("start", "node_get_basic_plant")
    workflow.add_edge("start", "node_get_basic_shelflife")
    workflow.add_edge("start", "node_get_basic_unit_measurements")

    workflow.add_edge("node_get_basic_plant", "checkpoint")
    workflow.add_edge("node_get_basic_shelflife", "checkpoint")
    workflow.add_edge("node_get_basic_unit_measurements", "checkpoint")

    workflow.add_edge("checkpoint", "node_productgroup_get_top_similarity")


    workflow.add_conditional_edges("node_productgroup_get_top_similarity", routing_new_variation)
    workflow.add_edge('node_is_newvariation', END)
    workflow.add_edge('node_productgroup_get_attributes', END)

    return workflow.compile()

