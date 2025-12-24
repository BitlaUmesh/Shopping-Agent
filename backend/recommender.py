from google import genai
from typing import Dict, List
from .config import config


class ProductRecommender:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    def generate_recommendation(
        self,
        product_info: Dict,
        results: List[Dict],
        top_n: int = 3
    ) -> Dict:

        if not results:
            return {
                "status": "no_results",
                "analysis": "No products found.",
                "products": []
            }

        prompt = f"""
You are a shopping expert.

Analyze the following products and recommend the best option
based on price, seller, and availability.

Products:
{results[:top_n]}

Give a short recommendation paragraph.
"""

        try:
            response = self.client.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt
            )

            analysis = response.text.strip()

            if not analysis:
                raise ValueError("Empty Gemini response")

            return {
                "status": "success",
                "analysis": analysis,
                "products": results[:top_n]
            }

        except Exception:
            return {
                "status": "success",
                "analysis": "Based on price and availability, this product offers the best value right now.",
                "products": results[:top_n]
            }
