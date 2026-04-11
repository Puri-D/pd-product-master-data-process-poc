import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st


class DataPersistenceManager: 

    @staticmethod
    def save_to_rag_examples(topic_config:Dict, input_source:str, extracted_data:Dict) -> str:

        try:
            # Read yaml topic file, get path and fields
            rag_config = topic_config['topic']['reference_data']['rag_examples']
            rag_path = rag_config['path']
            input_column = rag_config['schema']['embedding_column']
            field_names = list(topic_config['fields'].keys())


            # Read existing CSV or create new
            try:
                df = pd.read_csv(rag_path)
            except FileNotFoundError:
                # Create with dynamic columns from topic
                columns = [input_column] + field_names
                df = pd.DataFrame(columns=columns)

            # Build row dynamically based on topic fields
            new_row = {input_column: input_source}
            for field in field_names:
                new_row[field] = extracted_data.get(field)

            # Check if input already exists (update vs add)
            if input_source in df[input_column].values:
                idx = df[df[input_column] == input_source].index[0] #Replacing Existing record field by field
                for col, value in new_row.items():
                    df.at[idx, col] = value
                    action = "Updated"
            else:
                # Append new row
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                action = "Added"

            df.to_csv(rag_path, index=False, encoding='utf-8')
            st.cache_resource.clear()

            return action
        
        except Exception as e:
            raise Exception(f"Failed to save to RAG CSV: {str(e)}")

    

    @staticmethod
    def save_to_mdm(
        topic_name: str,
        input_source: str,
        extracted_data: Dict,
        correction_made: bool = False,
        mdm_file: str = "mdm_records.json",
        metadata:Dict = None,
    ) -> str:
        """
        Save to MDM records file (generic for all topics).
        
        Args:
            topic_name: Topic identifier (e.g., "unit_of_measurement", "storage_conditions")
            input_field_value: Source text that was extracted from
            extracted_data: Extracted field values {field_name: value}
            correction_made: Whether human corrections were applied
            mdm_file: Path to MDM JSON file (default: "mdm_records.json")
        
        Returns:
            str: Generated record ID (e.g., "UNIT_OF_MEASUREMENT-20250407-143022")
        
        Raises:
            Exception: If save fails
        
        Example:
            >>> record_id = DataPersistenceManager.save_to_mdm(
            ...     topic_name="unit_of_measurement",
            ...     input_field_value="2 kg/bag x 10 bags/carton",
            ...     data={'inner_weight_max': 2.0},
            ...     correction_made=True
            ... )
            >>> print(record_id)  # "UNIT_OF_MEASUREMENT-20250407-143022"
        """
        try:
            # Generate unique record ID
            record_id = f"{topic_name.upper()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Create MDM record
            record = {
                'record_id': record_id,
                'topic': topic_name,
                'extracted_data': extracted_data,
                'metadata': metadata
            }
            
            # Read existing records
            try:
                with open(mdm_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except FileNotFoundError:
                records = []
            
            # Append new record
            records.append(record)
            
            # Save back to file
            with open(mdm_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            
            return record_id
            
        except Exception as e:
            raise Exception(f"Failed to save to MDM: {str(e)}")
    
