import pandas as pd
import requests
import json


class LLMReranking:

    def __init__ (self,
                  model="llama3.1:8b"
                  ):
        
        self.model = model
        self.url = "http://localhost:11434"
        print(f"LLM initialized: {model}")

        #Load Product Group 1-6 Master as list --> self.pgmaster
        self.pgpath = r'E:\npd-master-data-poc\data\mas\mas_pg.csv'
        self.pgmaster = pd.read_csv(self.pgpath, encoding='utf-8')
        self.pgmaster = self.pgmaster.apply(lambda x: x.dropna().tolist()).to_dict()

        self.pg4_to_um = {
            'TRAY':'TRA',
            'BAG':'BAG',
            'SACHET':'SAC',
            'TANK':'TNK',
            'BOX':'BOX',
            'KG':'KG',
            'PALLET':'PAL',
            'CASE': 'CS',
            'CARTON':'CAR',
            'PACK':'PAC'
            }

    def classify(self, npd_data:dict, candidates:list[dict], master_df=None):
    
        #mgpath = r'E:\npd-master-data-poc\data\mas\mas_material_group.xlsx'
        #self._load_materialgroup(mgpath, npd_data.get('plant_group'))

        self._load_pgmaster()
        prompt = self._build_prompt(npd_data,candidates)
        response = self.call_llm(prompt)
        parsed_response = self._parse_response(response)
        return parsed_response

    def _load_pgmaster(self):
  
        #Make a PG1-6 list prompt --> self.pg_text_output
        line = []
        for key, values in self.pgmaster.items():
            setattr(self, key, values) 
            line.append(f"{key}:{values}")

        self.pg_text_output = "\n".join(line)


    def _load_materialgroup(self, mgpath, business_group): ## SKIP (it's a different beast)
        #Local Material Group Master
        matgroupmaster = pd.read_excel(mgpath)

        #!! Too large library, need to filter business group to pull only relevant codes 
        self.relevant_matgroup = matgroupmaster[matgroupmaster['species'].str.lower() == business_group.lower()][:20]
        
        self.matgrouplines = {}

        for _, row in self.relevant_matgroup.iterrows():
            code = row['material_group_code']
            nameth = row['material_group_name_th'].lower()

            self.matgrouplines[code] = nameth

        return self.matgrouplines

            

    def _build_prompt(self,
                      npd_data: dict = None, #dict input from ***test3 NOT dirty
                      top_candidate: list[dict] = None): #list of candidates in dict
        
        #Load all necessary keywords (pg and mg_fitler) into prompt format -> Load input data and candidates list -> Make prompt with keywords + input + candidate list

        
        #Struture NPD Message
        input_prompt = f""" You are a product classification expert for a food manufacturing company. 
        
        NEW PRODUCT TO CLASSIFY:
        Product Name: {npd_data['product_name']}
        Plant: {npd_data['plant_group']}
        Inner Unit: {npd_data['inner_container_um'] if npd_data['inner_container_um'] else None}
        Master Unit: {npd_data['master_container_um'] if npd_data['master_container_um'] else None}
        Storage: {npd_data['storage']}
        Business Unit: {npd_data['product_type']}
""" #DO NOT CHANGE NAME, LINK WITH DATA_PROCESS HARD CODED
        

        
        #Struture Product Candidate Message
        candidate_prompt = "\nTOP 5 REFERENCE PRODUCTS:\n"
        
        for i, c in enumerate(top_candidate[:2],1): #top3 SKIP Material Group (For now) Material Group Code: {c.get('material_group_code')} Material Group Name: {c.get('material_group_name')}
            candidate_prompt += f"""
        [{i}] 
        Score: {c.get('similarity')}
        Product Name: {c.get('material_name_local')}
        Product Code: {c.get('material_code')}
        PG1: {c.get('pg1')}
        PG2: {c.get('pg2')}
        PG3: {c.get('pg3')}
        PG4: {c.get('pg4')}
        PG5: {c.get('pg5')}
        PG6: {c.get('pg6')}
        """

        #Struture Product Group 1-6 Message
        pg_definitions_prompt = f"""
        VALID PG Definition and VALUES - USE ONLY THESE:
        PG1: Product Grade/Size -> {', '.join(self.pgmaster.get('pg1', [])[:15])}...
        PG2: Product Parts(Slaugther) or Process(Further/RTE) --> {', '.join(self.pgmaster.get('pg2', [])[:15])}...
        PG3: Main Product or By Product --> {', '.join(self.pgmaster.get('pg3', [])[:10])}...
        PG4: Product Packing Unit --> {', '.join(self.pgmaster.get('pg4', [])[:10])}...
        PG5: Product Storage or Usage --> {', '.join(self.pgmaster.get('pg5', [])[:10])}...
        PG6: Product Type --> {', '.join(self.pgmaster.get('pg6', [])[:10])}...
        """

        #Struture Material Group Message
        #mg_sample = list(self.matgrouplines.items())[:10]
        #formatted_output = "\n".join(f"{code}: {name}" for code, name in mg_sample)
        #mg_prompt = f"""MATERIAL GROUP EXAMPLE {formatted_output}"""

        prompt = f"""
        {input_prompt}

        {candidate_prompt}

        {pg_definitions_prompt}


1. Pick the BEST reference from above
   - Consider similarity score
   - Match storage type (FROZEN vs CHILL)
   - Match packing type (BAG vs VACUUM vs CARTON)
   - You MUST use ONLY the reference you selected.
   - DO NOT take PG values from other references.
   - If you copy a PG value, it MUST come from the reference you selected.

2. Start with that reference's PG1-6 values

3. Adjust ONLY where new product clearly differs:
   - PG4: If packing type different
   - PG5: If storage type different (If product name contains any REJECT, WIP, RAW use those instead)
   - PG6: If product type different
   - Keep PG1, PG2, PG3 from reference unless clearly wrong
   - DO NOT USE PG Values in any field other than its Numbeered PG Field

4. For material_group_code: use reference's code or suggest similar

CRITICAL RULES:
- MUST use exact values from "VALID PG VALUES" above
- NO field labels in values (WRONG: "PG2: SIRLOIN" | RIGHT: "SIRLOIN")
- DO NOT invent new values like "FOOD" or "UNSPECIFIED" or "PG2:FOOD"
- Return ONLY the JSON - no text before or after
- Fill ALL fields - no empty values
- If value equals reference_value, source MUST be "copied_from_reference"
- Only include "reason" when source is "adjusted_by_llm"
- ONLY include "reason" field when source is "adjusted_by_llm"
- ⚠ ABSOLUTELY NO COMMENTS - JSON does not support // or /* */ comments
- ⚠ Do NOT add explanations after field values
- ⚠ All string values MUST be in "quotes"
- ⚠ Use ONLY the JSON structure below - nothing else


Return ONLY VALID JSON FORMAT DO NOT ADD ANY COMMENTS AND EXPLANATION:

{{  "matched_product_code": "<product_code of the reference you chose>",
    "similarity": <similarity score of that reference>,
    "match_reasoning": "<1-2 sentences why you chose this reference>",
    "final_classification": {{
    "pg1": {{
      "value": "<insert pg1 value here>",
      "source": "<copied_from_reference OR adjusted_by_llm>",
      "reference_value": "<pg1 value from the reference product with highest similarity score>"
    }},
    "pg2": {{
      "value": "<insert pg2 value here>",
      "source": "<copied_from_reference OR adjusted_by_llm>",
      "reference_value": "<pg2 value from the reference product with highest similarity score>"
    }},
    "pg3": {{
      "value": "<insert pg3 value here>",
      "source": "<copied_from_reference OR adjusted_by_llm>",
      "reference_value": "<pg3 value from the reference product with highest similarity score>"
    }},
    "pg4": {{
      "value": "<insert pg4 value here>",
      "source": "<copied_from_reference OR adjusted_by_llm>",
      "reference_value": "<pg4 value value from the reference product with highest similarity score>",
      "reason": "<only include if source is adjusted_by_llm>"
    }},
    "pg5": {{
      "value": "<insert pg5 value here>",
      "source": <copied_from_reference OR adjusted_by_llm>",
      "reference_value": "<pg5 value from the reference product with highest similarity score>"
    }},
    "pg6": {{
      "value": <insert pg6 value here>",
      "source": "<copied_from_reference OR adjusted_by_llm>",
      "reference_value": "<pg6 value from the reference product with highest similarity score>"
    }}
  }}
}}"""
        return prompt
        



    def call_llm(self, prompt:str):

        try: 
            print("Asking LLM")
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt":prompt,
                    "stream": False,
                    "temperature":0.05,
                    "format": "json",
                    "repeat_penalty": 1.0,
                }
            )

            #response.raise_for_status()
            result = response.json()
            
            # Extract message content
            return result['response']
        
    
        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise


    def _parse_response(self, response):
        try:
            # Try direct parse
            return json.loads(response)
        
        except json.JSONDecodeError:
            # Try extracting from markdown
            print("Getting Response into Json")
            if "```json" in response:
                json_text = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_text = response.split("```")[1].split("```")[0].strip()
            elif "{" in response:
                # Extract just the JSON part
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]
            else:
                print("ERROR: Could not find JSON in response")
                print("Raw response:", response)
                return None
            
            try:
                return json.loads(json_text)
            except:
                print("ERROR: Could not parse JSON")
                print("Extracted text:", json_text)
                return None
            

            
    def _pg_confidence_score(self,
                       field_name:str,
                       field_value:str,
                       source_method:str,
                       npd_data:dict,
                       sim_score):
        
        score = float(sim_score)
        penalty = float(0.05) 

        #PG1 Validation Name Similarity (Parts Grade)
        if field_name == 'pg1': 
            
            if source_method == 'adjusted_by_llm':
                return score - penalty
            else: #copied form ref (Assuming its the same grade)
                return score

        #PG2 Validation Name Similarity (Parts)
        elif field_name == 'pg2': 

            if source_method == 'adjusted_by_llm':
                return score - penalty
            else: #copied form ref
                return score

        #PG3 #Name Similarity (Main/By)  
        elif field_name == 'pg3': 

            if source_method == 'adjusted_by_llm':
                return score - penalty
            else: #copied form ref
                return score


        #PG4 Validation Match with inner um
        elif field_name == 'pg4': 
            
            #Interpret PG4 value (PG4 -> MDM_UM)
            value = self.pg4_to_um.get('field_value')
            
            if value == npd_data['inner_container_um'] : 
                return sim_score 
            else:
                return 0.6

        #PG5 Validation Name Similaity + Storage
        elif field_name == 'pg5': 

            #Keyword Matching In Product Name   
            if "raw" in npd_data['product_name'].lower() and field_value == 'RAW':
                return 0.95
            
            elif 'reject' in npd_data['product_name'].lower() and field_value == 'REJECT':
                return 0.95
            
            elif 'wip' in npd_data['product_name'].lower() and field_value == 'WIP':
                return 0.95
            
            elif field_value in ['FROZEN', 'CHILL']:
                storage = npd_data['storage'].upper()
                if field_value == storage:
                    return 0.95
                else:
                    return 0.6
            else:
                return sim_score
                

                
        #PG6 Validation Name Similaity
        elif field_name == 'pg6': #PG6 - Business Group + Name Reasoning 
            product_type = npd_data['product_type'].upper()

            if field_value == product_type:
                return 0.95
            else:
                return 0.65
        
        else:
            return sim_score

    







    