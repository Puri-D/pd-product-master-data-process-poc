from typing import List, Dict

def tier3_llmrag_calculate_confidence(extracted_value:str, rag_similarity_score:List, value_lib:List = None):
    
    confidence = 1.0

    if rag_similarity_score:
        avg_similarity = sum(rag_similarity_score) / len(rag_similarity_score)
        rag_factor = avg_similarity
    else:
        rag_factor = 0.5

    if extracted_value is None: # Cross check with keywords
        completeness_factor = 0.3
    elif value_lib is not None and extracted_value in value_lib: #Value Found In 
        completeness_factor = 1.0
    else:
        completeness_factor = 0.7 #Unknown Value 

    consistency_factor = 1.0  #Default as 1.0

    confidence = (rag_factor * 0.4) + (completeness_factor * 0.4) + (consistency_factor * 0.2)

    return round(confidence,2)

def tier2_derived_calculate_confidence(field_name:str, depends_on_fields:List, extracted_data:Dict):

    missing = [dep for dep in depends_on_fields if extracted_data.get(dep) is None]

    if missing:
        return 0.0
    else: 
        dependency_confidences = [extracted_data.get(f'_metadata_{field}_confidence', 1.0) for field in depends_on_fields]

    return min(dependency_confidences)