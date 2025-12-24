import json
from google import genai
from typing import Dict
from .config import config

class ProductParser:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    def parse_query(self, user_query: str) -> Dict:
        prompt = f"""
Extract product details from this query and return ONLY valid JSON.

Query: "{user_query}"

Format:
{{
  "product": "",
  "brand": null,
  "model": null,
  "specifications": {{}},
  "budget": {{ "min": null, "max": null, "currency": "INR" }},
  "region": "India",
  "preferences": {{
    "price_priority": "lowest",
    "delivery_priority": true
  }}
}}
"""

        try:
            response = self.client.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt
            )

            result_text = response.text.strip()
            parsed = json.loads(result_text)
            parsed["search_query"] = user_query
            return parsed

        except Exception as e:
            print("Parser error:", e)
            return {
                "product": user_query,
                "search_query": user_query,
                "preferences": {"price_priority": "lowest", "delivery_priority": True},
                "region": config.DEFAULT_REGION
            }
