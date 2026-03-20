import requests #E:\PY\python.exe -m pip install requests
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity #distance

class LLMPackageParser:

    def __init__(self, UnitMaster=None, model="llama3.1:8b", rag_csv = None):
        self.model = model
        self.url = "http://localhost:11434"
        self.mapping = UnitMaster
        self.load_resources()
        self.rag_get()


    def load_resources(self): #classify unit code into quantity and weight unit list for LLM prompt

        #self.unit_list = self.mapping['mdm_unit_code'].tolist()
        #self.quantity_um_list = self.mapping[self.mapping['unit_type']=='Quantity']['mdm_unit_code'].tolist()
        #self.weight_um_list = self.mapping[self.mapping['unit_type']=='Weight']['mdm_unit_code'].tolist()


        json_path = r"data\keyword\um_th_en_translation.json"

        with open(json_path, 'r', encoding='utf-8') as f:
            self.trans_data = json.load(f)

        #Make rules for LLMs
        self.quantity_code = [] #[CS,PAC]
        self.weight_code = [] #[KG]
        self.text_to_code = {} #{'กล่อง':'CS', 'กิโล':'KG'}
        self.code_to_type = {} #{'CS':'Quantity', 'KG':'Weight'}
        self.translation = [] # [ {variation: 'กล่อง, box, etc', 'code':'CS'],.......]
            
        for item in self.trans_data:
            code = item['mdm_unit_code']
            type = item['unit_type'].lower()

            if type == 'quantity':
                self.quantity_code.append(code)

            elif type == 'weight':
                self.weight_code.append(code)
            
            self.code_to_type[code] = type

            for th in item['mdm_unit_text']['th']:
                th_clean = th.strip().lower()
                self.text_to_code[th_clean] = code # {'กล่อง':'CS'}

            for en in item['mdm_unit_text']['en']:
                en_clean = en.strip().lower()
                self.text_to_code[en_clean] = code # {'box':'CS'}

            self.translation.append({
                'variation': ', '.join(item['mdm_unit_text']['th'] + item['mdm_unit_text']['en']),
                'code': code
            })

    def rag_get(self):
        
        rag_path = r"E:\npd-master-data-poc\data\keyword\llm_rags_v2.csv"
        self.rag_df = pd.read_csv(rag_path, encoding='utf-8')
        self.rag_df = self.rag_df[self.rag_df['input_text'].notna()] #filter blank input_text
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')#generate embeddings
        self.rag_embed = self.embedder.encode(self.rag_df['input_text'].tolist())#generate embeddings
        
    def rag_find_sim(self,packing_text, get=3):
        
        input_embed = self.embedder.encode(packing_text)
        similar_embed = cosine_similarity([input_embed],self.rag_embed)[0]
        top_example = similar_embed.argsort()[-get:][::-1]

        self.top_similar = []
        for i in top_example:
            row = self.rag_df.iloc[i]
            self.top_similar.append({
                'similarity': float(similar_embed[i]),
                'input_text': row['input_text'],
                'item_qty': row['output_item_qty'] if pd.notna(row['output_item_qty']) else None,
                'item_unit': row['output_item_unit'] if pd.notna(row['output_item_unit']) else None,
                'item_weight_min': row['output_item_weight_min'] if pd.notna(row['output_item_weight_min']) else None,
                'item_weight_max': row['output_item_weight_max'] if pd.notna(row['output_item_weight_max']) else None,
                'inner_container_um': row['output_inner_container_um'] if pd.notna(row['output_inner_container_um']) else None,
                'item_per_inner_qty': row['output_item_per_inner_qty'] if pd.notna(row['output_item_per_inner_qty']) else None,
                'inner_weight_min': row['output_inner_weight_min'] if pd.notna(row['output_inner_weight_min']) else None,
                'inner_weight_max': row['output_inner_weight_max'] if pd.notna(row['output_inner_weight_max']) else None,
                'has_master': row['output_has_master'],
                'inner_per_master_qty': row['output_inner_per_master_qty'] if pd.notna(row['output_inner_per_master_qty']) else None,
                "master_weight_max": row['output_inner_per_master_qty'] * row['output_inner_weight_max'],
                "master_weight_min": row['output_inner_per_master_qty'] * row['output_inner_weight_min'],
                'master_container_um': row['output_master_container_um'] if pd.notna(row['output_master_container_um']) else None
            })

        return self.top_similar



    def create_prompt(self, packing_text): #make human prompt for LLM

        #list of quantity and weight unit codes
        quantity_codes_str = ', '.join(self.quantity_code)
        weight_codes_str = ', '.join(self.weight_code)
        
        #make tranlation summary "....." -> CS
        translation_summary = ""
        for items in self.translation:
            translation_summary += f"- [{items['variation']}] translate to {items['code']}\n"


        prompt = f"""You are a packing information extractor of food products for food manufacturing company.

        CRITICAL RULES:
        1. You must ONLY use unit codes from the allowed lists below
        2. Return ONLY valid JSON, no explanation, no markdown
        3. If you cannot extract a value, use null
        4. Do NOT invent or make up codes
        5. Usually, the text given i from smallest to largest packing level (item (commonly in pieces ชื่น) -> inner -> master) sometimes only item level is given or item + inner level
        6. Base unit is always KG (weight unit) for all products

        ALLOWED UNIT CODES:

        Quantity Units (for items and containers):
        {quantity_codes_str}

        Weight Units:
        {weight_codes_str}

        UNIT TRANSLATIONS (Thai/English → Code):
        {translation_summary}

        INPUT TEXT TO PARSE:
        "{packing_text}"

        OUTPUT FORMAT (JSON only, no markdown):
        {{
        "original_text": "<{packing_text}>,
        "base_unit": "<always kg, thus if any weight unit is given other than kg, convert to kg>",
        "item_qty": "<always 1>",
        "item_unit": "<should be in PCS, STK, (any animal parts) NOT PAC and BAG>",
        "item_weight_max": "<in kg only, if the weight value is given in range (example 10-20kg then use max value of 20, but if no range then use that value)>",
        "item_weight_min": "<in kg only, if the weight value is given in range (example 10-20kg then use min value of 10, but if no range then use that value)>",
        "inner_container_um": "<code from Quantity Units or None>",
        "item_per_inner_qty": "<number of item in inner container>",
        "inner_weight_max": "<calculate weight based on item_weight info",
        "inner_weight_min": "<calculate weight based on item_weight info",
        "has_master": "<true/false> based on if master level packing is given, if inner unit has a container",
        "inner_per_master_qty": "<number or None>",
        "master_container_um": "<code from Quantity Units or None>",
        "master_weight_max": "<simple calculation: inner per master * inner weight max>",
        "master_weight_min": "<simple calculation: inner per master * inner weight min>",
        }}"""

        similar_examples = self.rag_find_sim(packing_text)
        prompt += """ here are the examples with similar pattern to help you. you need to strictly follow them: \n"""

        for index, col in enumerate(similar_examples,1):
            prompt += f""" 
            
            Example {index} (similarity: {round(col['similarity'],3) * 100}%): 
            
            Input: "{col['input_text']}" \n
            Output: {{
            "base_unit": "KG",
            "item_qty": {col['item_qty']},
            "item_unit": "{col['item_unit']}",
            "item_weight_max": {col['item_weight_max']},
            "item_weight_min": {col['item_weight_min']},
            "inner_container_um": "{col['inner_container_um']}",
            "item_per_inner_qty": {col['item_per_inner_qty']},
            "inner_weight_max": {col['inner_weight_max']},
            "inner_weight_min": {col['inner_weight_min']},
            "has_master": {str(col['has_master']).lower()},
            "master_weight_max": {col['master_weight_max']},
            "master_weight_min": {col['master_weight_min']},
            "inner_per master_qty": {col['inner_per_master_qty']},
            "master_container_um": "{col['master_container_um']}"
            }}
            """
        
        prompt += f"""\n now extract from this input: {packing_text}"""
        return prompt


    def _llm_parser(self, packing_text):

        prompt = self.create_prompt(packing_text)

        response = requests.post(
            f"{self.url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0}
        )

        response_data = response.json()
        return response_data['response']
    
    