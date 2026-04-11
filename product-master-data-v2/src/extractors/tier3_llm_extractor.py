import importlib
from typing import Dict, List, Optional
from src.rag.similarity_engine import RAGSimilarityEngine
from src.utility.reference_loader import ReferenceDataLoader
from src.utility.prompt_builder import PromptBuilder
from src.utility.llm_client import OllamaClient 
from src.utility.confidence_cal import tier3_llmrag_calculate_confidence

class Tier3LLMExtractor:

    def __init__(self, topic_config:Dict):
    
        self.topic_config = topic_config
        self.topic_name = self.topic_config['topic']['name']
        self.topic_filename = self.topic_config['topic']['file']

        #Initialize Reference Data Loader ================================
        self.reference_loader = ReferenceDataLoader(self.topic_config)
        print(f"Topic References Loaded")

        #Initialize Prompt Builder
        self.prompt_builder = PromptBuilder(self.topic_config)
        print(f"Prompt Builder Initialized")

        #Initialize LLM tool ================================
        llm_config = topic_config['topic']['tier3_llm']
        self.llm_client = OllamaClient(
            model=llm_config['model'],
            base_url=llm_config['base_url'],
            timeout=llm_config['timeout']
        )
        print(f"LLM Initialized")
        
        #Check LLM methods ================================
        if 'rag' in llm_config: #Detect rag in yaml

            rag_config = llm_config['rag']
            rag_reference =  self.topic_config['topic']['reference_data']['rag_examples']
            
            rag_csv_path = rag_reference['path']
            embedding_column = rag_reference['schema']['embedding_column']

            #Initialize Similarity Engine
            self.similarity_engine = RAGSimilarityEngine(rag_csv_path=rag_csv_path,
                                                         embedding_model=rag_config['embedding_model'],
                                                         embedding_column=embedding_column)
            
            self.rag_top_k = rag_config.get('top_k_examples', 3)
            print(f"RAGSimilarityEngine initialized (top_k={self.rag_top_k}) ===================================================")

        else:
            self.similarity_engine = None 
            print(f"RAGSimilarityEngine Not Initialized (**RAG config not in topic yaml)) ===================================================")


        #Load Helpers and Formatters
        self._load_topic_modules()
        print("Topic modules loaded")

    # YAML Sensitive
    def _load_topic_modules(self):
        
        #Load Helpers Module
        helpers_module_path = f"config.topics.{self.topic_filename}.helpers"
        print (f"Loading {self.topic_name} Helpers/Formatters from {helpers_module_path}")

        self.helpers = importlib.import_module(helpers_module_path)

        if not hasattr(self.helpers, 'process_reference_data'):
            raise AttributeError(
                f"Module '{helpers_module_path}' must have function 'process_reference_data() check init or helpers.py to see if config has it'"
            )
        
        #Load Formatter Module
        formatters_module_path = f"config.topics.{self.topic_filename}.formatters"
        print (f"Loading {self.topic_name} Helpers/Formatters from {formatters_module_path}")

        formatters_module = importlib.import_module(formatters_module_path)

        #Get class Name =============================================== YAML important
        formatter_class_name = self._get_formatter_class_name()
        print(f"  Looking for formatter class: {formatter_class_name}")

        if not hasattr(formatters_module, formatter_class_name):
            raise AttributeError(
                f"Module '{formatters_module_path}' must have class '{formatter_class_name}'"
            )
    
        self.formatter_class = getattr(formatters_module, formatter_class_name)

    def _get_formatter_class_name(self) -> str:

        #Hardcoded Case
        if self.topic_name == 'Unit of Measurement':
            return "UOMReferenceFormatter"
        
        #General Case
        word = self.topic_filename.capitalize()
        return f'{word}ReferenceFormatter'
    
        #** This is important format to remember = CAPITAL(topic_filename("uom")) + "ReferenceFormatter" (i.e STORAGEReferenceFormatter, PLANTReferenceFormatter)


    def extract(self, field_names: List[str], source_data:Dict) -> Dict:

        source_field = self.topic_config['topic']['tier3_llm'].get(
            'source_text_field',
            'text'
        )

        print(f"\n{'='*80}")
        print("INITIALIZE: TIER3_LLM_EXTRACTION")
        print(f"{'='*80}")
        
        print(f"Topic: {self.topic_name}")
        print(f"Field To Extract: {field_names}")
        print(f"From source: {source_field}")

        input_text = source_data.get(source_field, '')

        if not input_text:
            print(f"ERROR: No '{source_field}' found in source_data")
            print(f"  Available fields in source_data: {list(source_data.keys())}") #list all of the raw data field in that record
            return {}
    
        print(f"Input text: '{input_text}'")


        # Reference Data Loading ===================================================

        reference_data_config = self.topic_config['topic']['reference_data']
        raw_reference_data = {}

        print(f"\n{'='*80}")
        print("STEP 1) LOADING REFERENCE DATA")
        print(f"{'='*80}")

        for ref_name in reference_data_config.keys():
            if ref_name != 'rag_examples':
                print(f"  Loading '{ref_name}'...")
                raw_reference_data[ref_name] = self.reference_loader.fetch(ref_name) #CAll ReferenceLoader class

            print(f"✓ Loaded {len(raw_reference_data)} reference dataset(s)")


        print(f"\n{'='*80}")
        print("STEP 2) PROCESSING REFERENCE DATA")
        print(f"{'='*80}")
        processed_data = self.helpers.process_reference_data(raw_reference_data)



        print(f"\n{'='*80}")
        print("STEP 3) FORMATTING FOR PROMPT")
        print(f"{'='*80}")
        formatted_text = self.formatter_class.format_reference_data(**processed_data)
        print(f"Formatted {len(formatted_text)} characters")
        reference_data = {'formatted_text': formatted_text}



        print(f"\n{'='*80}")
        print("STEP 4) RAG SIMILARITY SEARCH")
        print(f"{'='*80}")
        rag_examples = None

        if self.similarity_engine is not None:
            print(f"   Finding top {self.rag_top_k} similar examples...")
            rag_examples = self.similarity_engine.find_similar(
            input_text=input_text,
            top_k=self.rag_top_k
            )
            print(f"Found {len(rag_examples)} example(s)")

            for i, ex in enumerate(rag_examples, 1):
                print(f"  {i}. Similarity: {ex['similarity']:.3f} | Text: {ex['input_text'][:50]}...")

        else:
            print("  Skipping RAG (zero-shot mode)")


        print(f"\n{'='*80}")
        print("STEP 5) BUILDING PROMPT")
        print(f"\n{'='*80}")

        prompt = self.prompt_builder.build_extraction_prompt(
            field_names=field_names,
            input_text=input_text,
            rag_examples=rag_examples,
            reference_data=reference_data
        )

        print(prompt)
        print(f"✓ Prompt built: {len(prompt)} characters")
        
        print(f"\n{'='*80}")
        print("STEP 5) CALLING LLM")
        print(f"\n{'='*80}")

        temperature = self.topic_config['topic']['tier3_llm'].get("temperature",0.0)
        print(f"  Model: {self.llm_client.model}")
        print(f"  Temperature: {temperature}")
        print(f"  Waiting for response...")

        result = self.llm_client.generate(prompt, temperature=temperature)

        
        print(f"\n{'='*80}")
        print("RESULT")
        print(f"{'='*80}")

        if result:
            print(result)
            print(f"Extraction successful!")
            for field, value in result.items():
                print(f"  {field}: {value}")
            return result
        else:
            print("Extraction failed (LLM returned None)")
            return {}
