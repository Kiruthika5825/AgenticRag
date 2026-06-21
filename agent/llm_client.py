from openai import OpenAI
import logging
import os
from dotenv import load_dotenv
load_dotenv() 
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model_name: str = "meta/llama-3.1-8b-instruct"):
        self.model_name = model_name
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from LLM: {e}")
            raise