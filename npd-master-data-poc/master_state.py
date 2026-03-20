from typing import Optional, TypedDict, List, Dict

class MasterState(TypedDict):

    raw_input: str
    
    basic_view: dict
    basic_complete: bool
    basic_remark: str

    sales_view: dict
    sales_complete: bool

    #Production View
    prod_view: dict
    prod_complete: bool

    scm_view: dict
    scm_complete: bool




    