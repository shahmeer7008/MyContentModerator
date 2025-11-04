# File: llm_client.py
"""LLM client for interacting with Groq API."""

import os
import json
import httpx
from moderator import Config

class LLMClient:
    """Wrapper for Groq LLM interactions using direct API calls."""
    
    def __init__(self, api_key: str = None):
        """Initialize the LLM client."""
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = Config.GROQ_MODEL
        self.temperature = Config.TEMPERATURE
    
    def invoke(self, prompt: str) -> str:
        """Send a prompt to the LLM and get response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": 2000
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_detail = response.json().get("error", {}).get("message", "Unknown error")
                    raise Exception(f"Groq API error ({response.status_code}): {error_detail}")
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except httpx.TimeoutException:
            raise Exception("Request timed out. Please try again.")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected API response format: {str(e)}")
        except Exception as e:
            raise Exception(f"LLM invocation failed: {str(e)}")
    
    @staticmethod
    def set_api_key(api_key: str):
        """Set the Groq API key."""
        os.environ["GROQ_API_KEY"] = api_key