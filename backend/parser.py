"""
Product Parser Module
Extracts structured product information from natural language using Gemini LLM.
"""

import json
import google.generativeai as genai
from typing import Dict, Optional
from .config import config


class ProductParser:
    """Parse natural language product queries into structured format."""
    
    def __init__(self):
        """Initialize the parser with Gemini model."""
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        
    def parse_query(self, user_query: str) -> Dict:
        """
        Parse user query into structured product information.
        
        Args:
            user_query: Natural language product query
            
        Returns:
            Structured product information as dictionary
        """
        prompt = f"""
You are a product information extraction expert. Extract structured information from the user's product query.

User Query: "{user_query}"

Extract the following information and return ONLY a valid JSON object (no markdown, no additional text):

{{
  "product": "product name",
  "brand": "brand name or null",
  "model": "model/variant or null",
  "specifications": {{
    "storage": "storage capacity or null",
    "color": "color or null",
    "size": "size or null",
    "other": "any other specs"
  }},
  "budget": {{
    "min": minimum price or null,
    "max": maximum price or null,
    "currency": "currency code"
  }},
  "region": "country/region",
  "preferences": {{
    "price_priority": "lowest/best_value/premium",
    "delivery_priority": true/false,
    "seller_trust": "any/high/verified",
    "condition": "new/refurbished/any"
  }}
}}

Rules:
1. Use null for missing information
2. Infer reasonable defaults (e.g., region: "{config.DEFAULT_REGION}")
3. Return ONLY the JSON object, nothing else
4. Ensure valid JSON format
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up response (remove markdown if present)
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            
            # Parse JSON
            parsed_data = json.loads(result_text)
            
            # Add search query
            parsed_data["search_query"] = self._generate_search_query(parsed_data)
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {result_text}")
            # Return minimal structure
            return self._create_fallback_structure(user_query)
            
        except Exception as e:
            print(f"Error parsing query: {e}")
            return self._create_fallback_structure(user_query)
    
    def _generate_search_query(self, parsed_data: Dict) -> str:
        """Generate optimized search query for APIs."""
        parts = []
        
        if parsed_data.get("brand"):
            parts.append(parsed_data["brand"])
        
        if parsed_data.get("product"):
            parts.append(parsed_data["product"])
        
        if parsed_data.get("model"):
            parts.append(parsed_data["model"])
        
        specs = parsed_data.get("specifications", {})
        if specs.get("storage"):
            parts.append(specs["storage"])
        if specs.get("color"):
            parts.append(specs["color"])
        
        return " ".join(parts)
    
    def _create_fallback_structure(self, user_query: str) -> Dict:
        """Create minimal structure when parsing fails."""
        return {
            "product": user_query,
            "brand": None,
            "model": None,
            "specifications": {},
            "budget": {"min": None, "max": None, "currency": config.DEFAULT_CURRENCY},
            "region": config.DEFAULT_REGION,
            "preferences": {
                "price_priority": "lowest",
                "delivery_priority": True,
                "seller_trust": "any",
                "condition": "new"
            },
            "search_query": user_query
        }


if __name__ == "__main__":
    # Test the parser
    parser = ProductParser()
    
    test_queries = [
        "Find the cheapest iPhone 15 128GB in India with fast delivery",
        "Samsung Galaxy S23 under 50000 rupees",
        "Best laptop for gaming under $1500"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = parser.parse_query(query)
        print(json.dumps(result, indent=2))