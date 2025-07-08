import os
import logging
import aiohttp
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

class CultureModel:
    """
    Async wrapper around the Hugging Face API for the Mistral-7B-Instruct model.
    Specifically designed for culture and arts related questions.
    """
    
    def __init__(self):
        """Initialize the culture model with API configuration."""
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
        self.hf_token = os.getenv("HF_TOKEN")
        
        if not self.hf_token:
            logger.warning("HF_TOKEN not found in environment variables. API calls will likely fail.")
        
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        self.prompt_template = """You are CultureBot, an expert in world traditions, arts, humanities, and cultural practices across different regions and time periods. You provide informative, balanced, and educational responses about global cultural topics.

Q: {question}
A:"""

    async def get_answer(self, question: str) -> str:
        """
        Get an answer from the model for a given question.
        
        Args:
            question: The culture or arts related question to ask
            
        Returns:
            The model's response as a string
        """
        logger.info(f"Getting answer for question: {question}")
        
        # Format the prompt
        formatted_prompt = self.prompt_template.format(question=question)
        
        # Prepare the payload
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed with status {response.status}: {error_text}")
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                    
                    result = await response.json()
                    
                    # Extract the generated text
                    if isinstance(result, list) and len(result) > 0:
                        if "generated_text" in result[0]:
                            full_response = result[0]["generated_text"]
                            # Extract just the answer part (after "A:")
                            answer_parts = full_response.split("A:", 1)
                            if len(answer_parts) > 1:
                                answer = answer_parts[1].strip()
                            else:
                                answer = full_response.strip()
                            return answer
                        else:
                            logger.error(f"Unexpected API response format: {result}")
                            raise Exception(f"Unexpected API response format: {result}")
                    else:
                        logger.error(f"Unexpected API response: {result}")
                        raise Exception(f"Unexpected API response: {result}")
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to API: {str(e)}")
            raise Exception(f"Error connecting to API: {str(e)}")
