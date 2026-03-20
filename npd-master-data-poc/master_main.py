from master_workflow import build_master_workflow
import pandas as pd
from pprint import pprint

def single_row_process(raw_input:dict):
    #take raw input as dict, run through workflow, return result as dict
    initialize_workflow = build_master_workflow()

    result = initialize_workflow.invoke({
        "raw_input": raw_input
    })

    return result

def batch_load(path:str):
    raw_excel = pd.read_excel(path) #OR csv depending on input format, can be made dynamic with file extension check
    batch_result = []

    for _, row in raw_excel.iterrows():
        dict_row = row.to_dict()
        single_result = single_row_process(dict_row)
        batch_result.append(single_result)
        print(f"Processed row with ref: {dict_row.get('ref', 'NA')}")

    df_batch_result = pd.DataFrame(batch_result)
    return df_batch_result
        
    
if __name__ == "__main__":
    path = r'\npd-master-data-poc\rawinputtest.xlsx'
    test = batch_load(path)
    test.to_excel('langgraph_views_generation_result.xlsx', index=False) 

    
