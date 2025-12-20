"""
Recommender Module
Generates product recommendations using LLM analysis.
"""

import json
import google.generativeai as genai
from typing import Dict, List, Optional
from .config import config


class ProductRecommender:
    """Generate intelligent product recommendations."""
    
    def __init__(self):
        """Initialize the recommender with Gemini model."""
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    def generate_recommendation(
        self,
        product_info: Dict,
        search_results: List[Dict],
        top_n: int = 3
    ) -> Dict:
        """
        Generate product recommendation based on search results.
        
        Args:
            product_info: Original product query information
            search_results: List of search results
            top_n: Number of top recommendations
            
        Returns:
            Recommendation dictionary with analysis
        """
        if not search_results:
            return {
                "status": "no_results",
                "message": "No products found matching your criteria.",
                "recommendations": [],
                "analysis": ""
            }
        
        # Prepare data for LLM
        products_summary = self._prepare_products_summary(search_results[:top_n])
        user_intent = self._extract_user_intent(product_info)
        
        prompt = f"""
You are an expert shopping advisor. Analyze these product options and provide a recommendation.

USER REQUEST:
{user_intent}

AVAILABLE OPTIONS:
{products_summary}

Provide a comprehensive recommendation in the following JSON format:

{{
  "best_overall": {{
    "index": 0,
    "reason": "Why this is the best choice"
  }},
  "best_value": {{
    "index": 1,
    "reason": "Best price-to-quality ratio"
  }},
  "fastest_delivery": {{
    "index": 2,
    "reason": "Quickest availability"
  }},
  "analysis": "2-3 sentence overall analysis of the options",
  "considerations": ["Important factor 1", "Important factor 2"],
  "alternatives": "Brief mention of alternative options if any"
}}

Return ONLY the JSON, no markdown or additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up response
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            
            # Parse JSON
            recommendation = json.loads(result_text)
            
            # Add actual product details
            recommendation["products"] = search_results[:top_n]
            recommendation["status"] = "success"
            
            return recommendation
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._create_fallback_recommendation(search_results, top_n)
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return self._create_fallback_recommendation(search_results, top_n)
    
    def _prepare_products_summary(self, products: List[Dict]) -> str:
        """Prepare product summary for LLM."""
        summaries = []
        
        for i, product in enumerate(products):
            summary = f"""
Option {i + 1}:
- Product: {product.get('title', 'N/A')}
- Price: {product.get('price_string', 'N/A')}
- Seller: {product.get('seller', 'N/A')}
- Rating: {product.get('rating', 'N/A')} ({product.get('reviews', 'N/A')} reviews)
- Delivery: {product.get('delivery', 'N/A')}
- In Stock: {product.get('in_stock', True)}
"""
            summaries.append(summary.strip())
        
        return "\n\n".join(summaries)
    
    def _extract_user_intent(self, product_info: Dict) -> str:
        """Extract user intent as readable text."""
        parts = []
        
        parts.append(f"Looking for: {product_info.get('product', 'Product')}")
        
        if product_info.get('brand'):
            parts.append(f"Brand: {product_info['brand']}")
        
        specs = product_info.get('specifications', {})
        if specs:
            spec_parts = [f"{k}: {v}" for k, v in specs.items() if v]
            if spec_parts:
                parts.append(f"Specifications: {', '.join(spec_parts)}")
        
        budget = product_info.get('budget', {})
        if budget.get('max'):
            parts.append(f"Budget: Up to {budget['max']} {budget.get('currency', '')}")
        
        prefs = product_info.get('preferences', {})
        if prefs.get('price_priority'):
            parts.append(f"Priority: {prefs['price_priority']} price")
        if prefs.get('delivery_priority'):
            parts.append("Fast delivery preferred")
        
        return " | ".join(parts)
    
    def _create_fallback_recommendation(
        self,
        products: List[Dict],
        top_n: int
    ) -> Dict:
        """Create basic recommendation when LLM fails."""
        if not products:
            return {
                "status": "error",
                "message": "Unable to generate recommendations",
                "products": []
            }
        
        # Simple ranking by price and rating
        sorted_products = sorted(
            products[:top_n],
            key=lambda x: (-float(x.get('rating', 0) or 0), x.get('price', float('inf')))
        )
        
        return {
            "status": "success",
            "best_overall": {
                "index": 0,
                "reason": "Best combination of price and rating"
            },
            "analysis": f"Found {len(products)} options. Top recommendation based on price and ratings.",
            "products": sorted_products,
            "considerations": ["Price", "Seller rating", "Availability"]
        }


if __name__ == "__main__":
    # Test the recommender
    recommender = ProductRecommender()
    
    test_product_info = {
        "product": "iPhone 15",
        "brand": "Apple",
        "specifications": {"storage": "128GB"},
        "region": "India",
        "preferences": {"price_priority": "lowest", "delivery_priority": True}
    }
    
    test_results = [
        {
            "title": "Apple iPhone 15 128GB Blue",
            "price": 79900,
            "price_string": "₹79,900",
            "seller": "Amazon",
            "rating": 4.5,
            "reviews": "1,234",
            "delivery": "Free delivery by tomorrow",
            "url": "https://example.com"
        }
    ]
    
    print("Testing Recommender...")
    recommendation = recommender.generate_recommendation(test_product_info, test_results)
    print(json.dumps(recommendation, indent=2))