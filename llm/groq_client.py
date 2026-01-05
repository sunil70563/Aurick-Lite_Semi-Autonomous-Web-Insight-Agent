import os
from groq import Groq
from loguru import logger

class GroqLLM:
    """
    Wrapper for Groq API provided by the `groq` python library.
    Default Model: llama-3.1-70b-versatile
    """
    def __init__(self, model="llama-3.1-70b-versatile"):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=self.api_key)
        self.model = model

    def chat(self, messages, temperature=0.2):
        """
        Send a chat completion request to Groq.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            raise e
