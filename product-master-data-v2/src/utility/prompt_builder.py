from typing import List, Dict, Optional
import json
import pandas as pd

class PromptBuilder:

    def __init__(self, topic_config:Dict):

        self.topic_config = topic_config
        self.prompt_config = topic_config['topic']['prompt_config']
        self.tier3_config = topic_config['topic']['tier3_llm']
        self.fields_config = topic_config.get('fields', {})

    def build_extraction_prompt(self,
                                field_names: List[str],
                                input_text: str,
                                rag_examples: Optional[List[Dict]] = None,
                                reference_data: Optional[Dict] = None):
        
        prompt_parts = []

        # Part 1: System role
        prompt_parts.append(self._build_system_role())
        
        # Part 2: Task description
        prompt_parts.append(self._build_task_description())
        
        # Part 3: Critical instructions
        prompt_parts.append(self._build_critical_instructions())
        
        # Part 4: Field descriptions
        prompt_parts.append(self._build_field_descriptions(field_names))
        
        # Part 5: Reference data (if provided)
        if reference_data:
            prompt_parts.append(self._build_reference_data_section(reference_data))
        
        # Part 6: Examples (if RAG)
        if rag_examples:
            prompt_parts.append(self._build_examples_section(rag_examples, field_names))
        
        # Part 7: Zero-shot instructions (if no examples)
        if not rag_examples and 'zero_shot' in self.tier3_config:
            prompt_parts.append(self._build_zero_shot_instructions())
        
        # Part 8: Output format
        prompt_parts.append(self._build_output_format())
        
        # Part 9: Extraction header + input
        prompt_parts.append(self._build_extraction_section(input_text, field_names))
        
        # Join all parts with double newlines
        return "\n\n".join(prompt_parts)



# ===================================================
# Private Methods - Prompt Helper
# ===================================================

    def _build_system_role(self):
        return self.prompt_config.get('system_role', '').strip()
    
    # ==============================================================
    
    def _build_task_description(self):
        """Build task description section from config."""
        return self.prompt_config.get('task_description', '').strip()
    
    # ==============================================================

    def _build_critical_instructions(self):
        """Build critical instructions section from config."""
        instructions = self.prompt_config.get('critical_instructions', [])

        if not instructions:
            return ""
        
        parts = ["CRITICAL INSTRUCTION"]
        for item in instructions:
            parts.append(f"- {item}")

        return "\n".join(parts)
    

    # ==============================================================

    def _build_field_descriptions(self, field_names: List[str]):

        parts = ["FIELD TO EXTRACT"]

        for field in field_names:
            field_config = self.fields_config.get(field, {})
            description = field_config.get('description', 'No description')
            data_type = field_config.get('data_type', 'unknown')

            parts.append(f"- {field} ({data_type}): {description}")

        return "\n".join(parts)
    
    # ==============================================================

    
    def _build_reference_data_section(self, helper_data: Dict):

        parts = ["REFERENCE DATA"]

        # =========================================================================
        # This is very specific config for UOM reference data
        # =========================================================================

        if 'formatted_text' in helper_data:
            parts.append(helper_data['formatted_text'])
        
        else:
            for key, value in helper_data.items():
                if isinstance(value, (str, int, float)):
                    parts.append(f"{key}: {value}")
                elif isinstance(value, list) and len(value) < 20:
                    parts.append(f"{key}: {', '.join(map(str, value))}")
        
        return "\n\n".join(parts)
    

    # ==============================================================

    def _build_examples_section(self, 
                                rag_examples: List[Dict],
                                field_names: List[str]) -> str:
        parts = []
        
        # Add examples header from config
        header = self.prompt_config.get('examples_header', 'EXAMPLES:')
        parts.append(header.strip())
        
        # Add each example
        for i, example in enumerate(rag_examples, 1):
            # Input text
            input_text = example.get('input_text', 'N/A')
            similarity = example.get('similarity', 0)
            
            parts.append(f"\nExample {i} (similarity: {similarity:.2f}):")
            parts.append(f'Input: "{input_text}"')
            
            # Output (only show requested fields)
            output_parts = []
            for field_name in field_names:
                output_key = field_name
                
                if output_key in example:
                    value = example[output_key]
                    output_parts.append(f'  "{field_name}": {self._format_value(value)}')

            #Format output for prompt
            if output_parts:
                parts.append("Output: {")
                parts.extend(output_parts)
                parts.append("}")
        
        return "\n".join(parts)
    
    # ==============================================================

    def _build_zero_shot_instructions(self) -> str:
        zero_shot_config = self.tier3_config.get('zero_shot', {})
        additional_instructions = zero_shot_config.get('additional_instructions', [])
        
        if not additional_instructions:
            return ""
        
        parts = ["ADDITIONAL GUIDANCE (no examples provided):"]
        
        # Handle both list and single string
        if isinstance(additional_instructions, list):
            for instruction in additional_instructions:
                parts.append(f"- {instruction}")
        else:
            parts.append(f"- {additional_instructions}")
        
        return "\n".join(parts)
    

    # ==============================================================

    def _build_output_format(self) -> str:
        """Build output format instructions from config."""
        return self.prompt_config.get('output_format_instructions', '').strip()
    
    # ==============================================================

    def _build_extraction_section(self, 
                                  input_text: str,
                                  field_names: List[str]) -> str:

        parts = []
        
        # Add extraction header from config
        header = self.prompt_config.get('extraction_header', 'NOW EXTRACT:')
        parts.append(header.strip())
        
        # Add input text
        parts.append(f'Input text: "{input_text}"')
        
        # Remind which fields to extract
        parts.append(f'Extract these fields: {", ".join(field_names)}')
        
        return "\n".join(parts)
    
    # ==============================================================

    def _format_value(self, value) -> str:


        if value is None or (isinstance(value, float) and pd.isna(value)):
            return "null"
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)