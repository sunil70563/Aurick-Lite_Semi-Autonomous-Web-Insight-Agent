import os
import json
from typing import List, Dict, Any, Optional
from groq import Groq
from loguru import logger

class GroqClient:
    """
    Wrapper for Groq API to handle reasoning and JSON structured outputs.
    Default Model: llama-3.1-70b-versatile
    """
    def __init__(self, model: str = "llama-3.1-70b-versatile", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model

    def complete(self, messages: List[Dict[str, str]], temperature: float = 0.2, json_mode: bool = False) -> str:
        """
        Send messages to Groq and return the content.
        """
        try:
            response_format = {"type": "json_object"} if json_mode else None
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format=response_format
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            raise e

    def get_json(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
        """
        Get structured JSON response from Groq.
        """
        content = self.complete(messages, temperature=temperature, json_mode=True)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Groq response: {content[:100]}...")
            raise e
