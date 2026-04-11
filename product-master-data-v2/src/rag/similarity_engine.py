import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


class RAGSimilarityEngine:
    """
    Universal RAG similarity matcher using sentence embeddings.
    
    YOUR EXISTING LOGIC: Embedding-based similarity matching
    Works for any topic - just provide different RAG corpus.
    """
    
    def __init__(self, 
                 rag_csv_path: str,
                 embedding_model: str = 'all-MiniLM-L6-v2',
                 embedding_column: str = None):
        
    #======================================================
    # 1) Load RAG sample data and embedding all of records 
    #======================================================

        self.rag_df = pd.read_csv(rag_csv_path, encoding='utf-8')
        self.embedding_column = embedding_column
        self.rag_df = self.rag_df[self.rag_df[embedding_column].notna()] # Remove NA record

        print(f"Loading RAG corpus from: {rag_csv_path}")
        print(f"  Embedding column: {embedding_column}")
        print(f"  Found {len(self.rag_df)} examples")
        
        # Initialize embedder
        self.embedder = SentenceTransformer(embedding_model)
        
        # Pre-compute embeddings
        print(f"Computing embeddings for {len(self.rag_df)} RAG examples...")
        self.rag_embeddings = self.embedder.encode(
            self.rag_df[embedding_column].tolist(),
            show_progress_bar=True
        )

        print("Success: RAG embeddings ready")
        
        self._last_similarities = []


    #======================================================
    # 1) Load RAG sample data and embedding all of records 
    #======================================================

    def find_similar(self,
                     input_text:str,
                     top_k:int = 3):
        

        input_embedding = self.embedder.encode([input_text])[0]

        similarities = cosine_similarity([input_embedding], self.rag_embeddings)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            row = self.rag_df.iloc[idx]

            result = {
                'similarity': float(similarities[idx]),
                **row.to_dict()
            }
            results.append(result)
            
        self._last_similarities = [result['similarity'] for result in results]
    
        return results
            