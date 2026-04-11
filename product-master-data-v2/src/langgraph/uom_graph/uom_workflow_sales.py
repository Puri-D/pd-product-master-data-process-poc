from langgraph.graph import StateGraph, END
from .uom_state import UOMExtractionState
from .uom_nodes import transform_sales_node


def build_sales_workflow():
    """
    Sales View Transformation Workflow.
    
    Flow:
    1. Transform Production + MDM → Sales View
    2. END (wait for human approval)
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(UOMExtractionState)
    
    # Add node
    workflow.add_node("transform_sales", transform_sales_node)
    
    # Define flow
    workflow.set_entry_point("transform_sales")
    workflow.add_edge("transform_sales", END)
    
    return workflow.compile()