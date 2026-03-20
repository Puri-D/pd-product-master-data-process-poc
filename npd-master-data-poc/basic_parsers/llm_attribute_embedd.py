import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os

class EmbeddingStorage:

    def __init__(self, storage_path):
         self.storage_path = storage_path
         self.embedd_info = None 
         self.metadata = None
     
    def save(self, embed, metadata): # Save new product_master embedding file into storage path
        os.makedirs(os.path.dirname(self.storage_path) if os.path.dirname(self.storage_path) else '.',exist_ok= True)

        with open(self.storage_path, 'wb') as f:
            pickle.dump({
                'embeddings' : embed,
                'metadata': metadata.to_dict('records')   
            }, f)
     
    def load(self): 
         
        if not os.path.exists(self.storage_path): #Load existing embedding file from storage path
             print(f'No embeddings found at {self.storage_path}')
             return None, None
         
        with open(self.storage_path, 'rb') as f:
             data = pickle.load(f)

        embbedding = data['embeddings']
        metadata = pd.DataFrame(data['metadata'])

        return embbedding, metadata

    def exists(self): #check is embeddings is there (True/False)
        return os.path.exists(self.storage_path)
        

class EmbeddingSearch:
    
    def __init__(self,
                 model:str = 'paraphrase-multilingual-MiniLM-L12-v2',
                 storage_path:str = None): ###*** Add embed path later
        
        #Load Model
        self.model = SentenceTransformer(model)
        #dimension = self.model.get_sentence_embedding_dimension()


        #Initialize Storage
        self.storage = EmbeddingStorage(storage_path)
        
        
        print("Embedding Cache Loaded!")

        #Place to populated loaded embeddings
        self.product_embed = None
        self.product_data = None
       

    def embed_all_products(self, mas_product_df, text_column = 'material_name_local', force_recompute = False):
        

        #If we have stored product_desc embeddings -> load it!
        if not force_recompute and self.storage.exists():
            self.product_embed, self.product_data = self.storage.load()
            return
        
        #if we need to recompute

        #get all produce_desc into list
        texts = mas_product_df[text_column].tolist()

        self.product_embed = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True)
        
        self.product_data = mas_product_df
        
        self.storage.save(
            self.product_embed,
            self.product_data
            ) # save mas_product embedding into storage


    def embed_cosine_similar(self, input_vector, corpus):
        dot_products = np.dot(corpus, input_vector)
        query_norm = np.linalg.norm(input_vector)
        corpus_norms = np.linalg.norm(corpus, axis=1)
        similarities = dot_products / (corpus_norms * query_norm + 1e-8)

        return similarities

    
    
    
    def embed_search(self, input:str, mas_filtered_df = None, top_n = None): #Input text and match with embedded filtered products -> List[Dict]
        
        if self.product_embed is None:
            raise ValueError("Must call embed_all_products() first!")
        
        
        #Embed the input text (dirty data)
        query_embedding = self.model.encode(input, convert_to_numpy=True)

        if mas_filtered_df is not None:
            filtered_code = set(mas_filtered_df['material_code'].tolist())
            all_code = self.product_data['material_code'].tolist()

            search_indices = [i for i, code in enumerate(all_code) if code in filtered_code]
            
            search_embedding = self.product_embed[search_indices]

        else:
            search_indices = list(range(len(self.product_embed)))
            search_embedding = self.product_embed


        similarity = self.embed_cosine_similar(query_embedding, search_embedding)
        top_index = np.argsort(similarity)[::-1][:top_n]
        
        matches = []

        for rank, index in enumerate(top_index, 1):
            original_idx = search_indices[index]
            product_row = self.product_data.iloc[original_idx]

            result = {
                'rank': rank,
                'material_code': product_row['material_code'],
                'material_name_local': product_row['material_name_local'],
                'similarity': float(similarity[index]),
            }

            for col in product_row.index:
                if col not in result:
                    result[col] = product_row[col]

            matches.append(result)

        return matches 

