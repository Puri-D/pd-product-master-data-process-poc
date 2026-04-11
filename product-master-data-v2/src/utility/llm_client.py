import requests
import json
import time  
from typing import Dict, Optional, List, Any

class OllamaClient:
    """
    Universal LLM client for Ollama API.
    
    YOUR EXISTING LOGIC: Ollama API wrapper with error handling
    """
    
    def __init__(self, 
                 model: str = "llama3.1:8b",
                 base_url: str = "http://localhost:11434",
                 timeout: int = 60): #default setting (if no topic loaded)

        self.model = model
        self.base_url = base_url
        self.timeout = timeout

        
    def generate(self, 
                 prompt: str,
                 temperature: float = 0.0,
                 format: str = "json",
                 max_retries: int = 3):  # Max retry

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": temperature,
                        "format": format
                    },
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                data = response.json()
                
            
                return self._parse_json(data.get('response', ''))
            
            except requests.exceptions.Timeout:

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"Timeout, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'error': f"Timeout after {max_retries} attempts",
                        'response': None
                    }
            
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"equest error: {str(e)}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.stats['errors'] += 1
                    return {
                        'success': False,
                        'error': f"Failed after {max_retries} attempts: {str(e)}",
                        'response': None
                    }
            
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f"Failed to parse response: {str(e)}",
                    'response': None
                }
    
    # =================================================================================

    def _parse_json(self, response_text: str):

        cleaned = response_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Try to parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"Failed: JSON parse error: {e}")
            print(f"Response text: {cleaned[:200]}...")
            return None
    