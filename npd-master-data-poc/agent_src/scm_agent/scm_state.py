from typing import TypedDict, List, Dict, Optional

#State need to have what the output has to be

class SCMState(TypedDict):

    mdm_data: dict

    #Temperature control
    temp_range: Optional[str]
    critical_point: Optional[str]
    risk_category: Optional[str]
    reasoning: Optional[str]


    
