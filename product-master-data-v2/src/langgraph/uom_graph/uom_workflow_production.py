from langgraph.graph import StateGraph, END
from .uom_state import UOMExtractionState
from .uom_nodes import transform_production_node


def build_production_workflow():
    """
    Production View Transformation Workflow.
    
    Flow:
    1. Transform MDM canonical → Production View
    2. END (wait for human approval)
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(UOMExtractionState)
    
    # Add node
    workflow.add_node("transform_production", transform_production_node)
    
    # Define flow
    workflow.set_entry_point("transform_production")
    workflow.add_edge("transform_production", END)
    
    return workflow.compile()