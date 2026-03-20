from langgraph.graph import StateGraph, END
from .scm_state import SCMState
from .scm_nodes import (
    llm_generate_temperature_control
)

def build_scm_workflow():
    workflow = StateGraph(SCMState)

    workflow.add_node(
        "temperature_info",             
        llm_generate_temperature_control 
    )

    workflow.set_entry_point("temperature_info")
    workflow.add_edge("temperature_info", END)

    app = workflow.compile()
    
    return app   





 
