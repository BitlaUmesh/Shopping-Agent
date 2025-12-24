from google import genai
from typing import Dict
from .config import config
from .vector_db import VectorDatabase


class ShoppingAssistant:
    def __init__(self, context: Dict = None):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.context = context or {}

    def chat(self, message: str) -> str:
        prompt = f"""
You are a helpful shopping assistant.

Context:
{self.context}

User: {message}

Give a clear, helpful answer.
"""
        try:
            response = self.client.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt
            )
            return response.text
        except Exception:
            return "Sorry, I couldn't process that right now."


class ResearchAssistant:
    def __init__(self, vector_db: VectorDatabase = None):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.vector_db = vector_db

    def chat(self, message: str) -> str:
        prompt = f"""
You are a research assistant specializing in product comparison.

User question:
{message}

Answer clearly and objectively.
"""
        try:
            response = self.client.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt
            )
            return response.text
        except Exception:
            return "Sorry, I couldn't process that right now."