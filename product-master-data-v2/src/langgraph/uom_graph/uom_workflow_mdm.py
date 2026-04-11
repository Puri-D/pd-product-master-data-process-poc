from langgraph.graph import StateGraph, END
from .uom_state import UOMExtractionState
from .uom_nodes import (
    extract_tier3_node,
    derive_fields_node,
)


def build_mdm_workflow():
    """
    Build the UOM extraction workflow graph.
    
    Flow:
    1. Extract Tier 3 fields (LLM)
    2. Derive calculated fields
    3. Display results
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(UOMExtractionState)
    
    # Add nodes
    workflow.add_node("extract_tier3", extract_tier3_node)
    workflow.add_node("derive_fields", derive_fields_node)
    
    # Define flow
    workflow.set_entry_point("extract_tier3")
    workflow.add_edge("extract_tier3", "derive_fields")
    workflow.add_edge("derive_fields", END)
    
    return workflow.compile()