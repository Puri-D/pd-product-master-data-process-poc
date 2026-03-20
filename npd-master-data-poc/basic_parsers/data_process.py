import pandas as pd
import json
from datetime import datetime

from .llm_um_parse import LLMPackageParser
from .plant_parse import PlantLoad
from .shelflife_parse import get_shelf_life
from .llm_attribute_hardfilter import Hardfilter
from .llm_attribute_embedd import EmbeddingSearch
from .llm_attribute_reranking import LLMReranking

class NPDprocessor: 

    def __init__(self):
        
        #Load RAG dataset
        rag_dataset = r"E:\npd-master-data-poc\data\keyword\llm_rags_v2.csv"
        self.packing_parser = LLMPackageParser(rag_csv=rag_dataset)
        
        #Load Plant parser
        self.plant_parser = PlantLoad()

        #Load shelf life parser
        self.shelf_parser = get_shelf_life()


        mas_product_path = r'E:\npd-master-data-poc\data\mas\mas_product.csv'
        self.mas_product = pd.read_csv(mas_product_path, encoding='utf-8')
        self.hardfilter = Hardfilter(mas_product_path)

        #Setting up Embedding Storage Path
        cache_path = r'E:\npd-master-data-poc\data\cache\mas_product_embeddings\poc_embeddings.pkl'
        self.embedsearch = EmbeddingSearch(storage_path = cache_path)
        self.embedsearch.embed_all_products(self.mas_product)

        self.llm_attribute = LLMReranking()


        #print("All Parsers Active")
        


    #Extract unit informaton from text
    def _packing_process(self, packing_text):

        #Check if empty
        if pd.isna(packing_text) or packing_text.strip() == "":
            return {
                'parsed': False,
                'confidence': 0,
                'error': "Does not have packing description"
            }
        
        #Use LLM to get data
        try:
            result = self.packing_parser._llm_parser(packing_text).strip()
            data = json.loads(result)
            df = pd.DataFrame([data]).to_dict(orient='list')
            clean_df = {k: v[0] if isinstance(v,list) else v for k,v in df.items()}
            return clean_df

        except Exception as e:
            return {
                'parsed': False,
                'confidence': 0,
                'error': e
            }
        
    
    def _plant_process(self, plant_text):

        if pd.isna(plant_text) or (plant_text).strip() == "":
            return {
                'parsed': False,
                'confidence': 0,
                'error': "Does not have plant description"
            }
        

        try:
            match_group = self.plant_parser.get_plant_group(plant_text)
            match_province = self.plant_parser.get_province(plant_text)
            match_district = self.plant_parser.get_district(plant_text)
            match_result = self.plant_parser.fuzzy_match_loc(plant_text, match_group, match_district, match_province)

            if match_result:
                best_match = match_result[0]

                return {
                    'plant_name': best_match[0],
                    'plant_group': match_group if match_group else None,
                    'confidence': best_match[1]
                }
            
            else:
                return {
                    'parsed': False,
                    'confidence': 0,
                    'error': 'No plant in mdm matched with text'
                }
            
        except Exception as e:
            return {
                    'parsed': False,
                    'confidence': 0,
                    'error': e
                }
    
    
    def _shelf_process(self, shelf_text):
        
        if pd.isna(shelf_text) or (shelf_text).strip() == "":
            result = ["NA", "NA"]
            return result
 
        
        try:
            result = self.shelf_parser.shelf_life_parser(shelf_text)
            result_conversion = self.shelf_parser.convert_to_day(result)
            return result_conversion

        except Exception as e:
            return {
                'parsed': False,
                'confidence': 0,
                'error': e
            }
        

    
    def _single_row_process (self, row):
        
        if hasattr(row, 'to_dict'):
            data = row.to_dict()
        else:
            data = row
        
        packing_result = self._packing_process(data.get('packing_detail'))
        plant_result = self._plant_process(data.get('plant'))
        shelf_result = self._shelf_process(data.get('shelf_life'))

        #General data
        product_name = data.get('product_name')
        inner_net_weight = data.get('inner_net_weight')
        id = data.get('ref')
        storage = data.get('temp')
        product_type = data.get('product_type')


        try:
            result = { ### DO NOT CHANGE NAMING IT WILL RUIN ATTRIBUTION

                #general
                'tmp_ref_id': id, 
                'product_name': product_name, #DO NOT CHANGE COLUMN NAME
                'material_name_local': product_name,
                'material_name_eng': product_name,
                'storage': storage, #DO NOT CHANGE COLUMN NAME
                'tmp_inner_net_weight': inner_net_weight,
                'product_type': product_type,
                
                #um info
                #'original_um_text': packing_result.get('original_text') if packing_result else None, #will remove
                'packing_desc': data.get('packing_detail'),
                'item_qty': packing_result.get('item_qty') if packing_result.get('item_qty') else None,
                'item_unit': packing_result.get('item_unit') if packing_result.get('item_unit') else None,
                'base_unit': packing_result.get('base_unit') if packing_result.get('base_unit') else None,
                'item_weight_min': packing_result.get('item_weight_min') if packing_result.get('item_weight_min') else None,
                'item_weight_max': packing_result.get('item_weight_max') if packing_result.get('item_weight_max') else None,
                'item_per_inner_qty': packing_result.get('item_per_inner_qty') if packing_result.get('item_per_inner_qty') else None,
                'inner_container_um': packing_result.get('inner_container_um') if packing_result.get('inner_container_um') else None, #DO NOT CHANGE NAME
                'inner_weight_min': inner_net_weight if packing_result.get('inner_weight_min') == None else packing_result.get('inner_weight_min'),
                'inner_weight_max': inner_net_weight if packing_result.get('inner_weight_max') == None else packing_result.get('inner_weight_max'),
                'has_master': packing_result.get('has_master') if packing_result.get('has_master') else None,
                'inner_per_master_qty': packing_result.get('inner_per_master_qty') if packing_result.get('inner_per_master_qty') else None,
                'master_weight_min': packing_result.get('master_weight_min') if packing_result.get('master_weight_min') else None,
                'master_weight_max': packing_result.get('master_weight_max') if packing_result.get('master_weight_max') else None,
                'master_container_um': packing_result.get('master_container') if packing_result.get('master_container') else None, #DO NOT CHANGE NAME
                'um_quality': None, #method calculation here
                'is_weigthed': True if packing_result.get('item_weight_min') != packing_result.get('item_weight_max') and product_type.lower() == 'swine' else False, #if item weight exist and not equal weigthed
                
                #plant info
                #'original_plant_text': row['plant'], #will remove
                'plant_name': plant_result.get('plant_name') if plant_result.get('plant_name') else None, 
                'plant_group': plant_result.get('plant_group') if plant_result.get('plant_group') else None, #AKA business group
                'plant_confidence': plant_result.get('confidence') if plant_result.get('confidence') else None, #based on fuzzy 

                #shelf life
                'shelf_life_day': shelf_result[0],
                'shelf_life_unit': shelf_result[1],

            }

            ####################### ATTRIBUTE ASSIGNMENT PROCESS ##############################
            
            #Hardfilter Dataframe
            filtered_sample = self.hardfilter.filter_sample_pool(result.get('plant_group'), result.get('product_type'))
        

            #Product Name Embedding, Get top 3 with most similar name
            embedded_sample = self.embedsearch.embed_search(
                result.get('product_name'),
                filtered_sample,
                top_n = 5
                ) 

            
            # def _check_simscore(self): #Check Top Result Similarity Score -> High Use as Ref -> Inv Score) / Low Flag as New Variation -> NORMAL INPUT 
            embedd_sample_topscore = [item['similarity'] for item in embedded_sample][0]

            if embedd_sample_topscore <= 0.75: 
                
                result.update({
                "pg1":  None,
                "pg2":  None,
                "pg3":  None,
                "pg4":  None,
                "pg5":  None,
                "pg6":  None,
                "top_n_list": None,
                "all_att": None,
                "varflag": "new_variation" #flag as new variation (needs human input)
                })

                return result
                
            
            else: #High scored sample -> initiate LLMs to classify product attributes

                #Reranking and Assign Attributes
                npd_attribute = self.llm_attribute.classify(result, embedded_sample, master_df=None)

                #Update the result
                result.update({
                    "pg1":  npd_attribute['final_classification']['pg1']['value'],
                    "pg2":  npd_attribute['final_classification']['pg2']['value'],
                    "pg3":  npd_attribute['final_classification']['pg3']['value'],
                    "pg4":  npd_attribute['final_classification']['pg4']['value'],
                    "pg5":  npd_attribute['final_classification']['pg5']['value'],
                    "pg6":  npd_attribute['final_classification']['pg6']['value'],
                    #"material_group_code": npd_attribute['final_classification'].get('material_group_code')
                    #"top_n_list": embedded_sample,
                    #"all_att": npd_attribute,
                    "varflag": "suggested",
                    "pg1_score": self.llm_attribute._pg_confidence_score("pg1",
                                                                         npd_attribute['final_classification']['pg1']['value'],
                                                                         npd_attribute['final_classification']['pg1']['source'],
                                                                         npd_data=result,
                                                                         sim_score=npd_attribute['similarity']),
                    "pg2_score": self.llm_attribute._pg_confidence_score("pg2",
                                                                         npd_attribute['final_classification']['pg2']['value'],
                                                                         npd_attribute['final_classification']['pg2']['source'],
                                                                         npd_data=result,
                                                                         sim_score=npd_attribute['similarity']),
                    "pg3_score": self.llm_attribute._pg_confidence_score("pg3",
                                                                         npd_attribute['final_classification']['pg3']['value'],
                                                                         npd_attribute['final_classification']['pg3']['source'],
                                                                         npd_data=result,
                                                                         sim_score=npd_attribute['similarity']),
                    "pg4_score": self.llm_attribute._pg_confidence_score("pg4",
                                                                         npd_attribute['final_classification']['pg4']['value'],
                                                                         npd_attribute['final_classification']['pg4']['source'],
                                                                         npd_data=result,
                                                                         sim_score=npd_attribute['similarity']),
                    "pg5_score": self.llm_attribute._pg_confidence_score("pg5",
                                                                         npd_attribute['final_classification']['pg5']['value'],
                                                                         npd_attribute['final_classification']['pg5']['source'],
                                                                         npd_data=result,
                                                                         sim_score=npd_attribute['similarity']),
                    "pg6_score": self.llm_attribute._pg_confidence_score("pg6",
                                                                         npd_attribute['final_classification']['pg6']['value'],
                                                                         npd_attribute['final_classification']['pg6']['source'],
                                                                         npd_data=result,
                                                                         sim_score=npd_attribute['similarity']),
                })


            return result

            
        except Exception as e:
            return e
    

    
    def _batch_process(self, dirty_path):
        
        #make it flexible to input (json, dict, etc) but currently just excel for testing
        excel_dirty = pd.read_excel(dirty_path)
        batch_result = []

        for _ , row in excel_dirty.iterrows():


            single_result = self._single_row_process(row)
            batch_result.append(single_result)


        df_clean_result = pd.DataFrame(batch_result)

        return df_clean_result
            


"""if __name__ == "__main__":
    NPDprocessor = NPDprocessor()
    test = NPDprocessor._batch_process(r'data/input/dirty_test.xlsx')
    print(test)
    test.to_excel('test3.xlsx', index=False)"""

