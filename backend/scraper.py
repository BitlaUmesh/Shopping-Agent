"""
Price Scraper Module
Fetches product prices from multiple sources using SERP API.
"""

import json
import time
from typing import Dict, List, Optional
from serpapi import GoogleSearch
from .config import config


class PriceScraper:
    """Scrape prices from multiple sources."""
    
    def __init__(self):
        """Initialize the scraper with API key."""
        self.api_key = config.SERPAPI_KEY
        
    def search_google_shopping(self, product_info: Dict) -> List[Dict]:
        """
        Search Google Shopping for product prices.
        
        Args:
            product_info: Parsed product information
            
        Returns:
            List of product results with prices
        """
        search_query = product_info.get("search_query", product_info.get("product", ""))
        region = product_info.get("region", config.DEFAULT_REGION)
        
        # Map region to location
        location_map = {
            "India": "India",
            "USA": "United States",
            "United States": "United States",
            "UK": "United Kingdom",
            "United Kingdom": "United Kingdom",
        }
        
        location = location_map.get(region, region)
        
        params = {
            "engine": "google_shopping",
            "q": search_query,
            "location": location,
            "api_key": self.api_key,
            "num": config.MAX_RESULTS
        }
        
        try:
            print(f"🔍 Searching Google Shopping for: {search_query}")
            search = GoogleSearch(params)
            results = search.get_dict()
            
            shopping_results = results.get("shopping_results", [])
            
            # Parse and normalize results
            normalized_results = []
            for item in shopping_results:
                normalized_item = self._normalize_google_shopping_result(item)
                if normalized_item:
                    normalized_results.append(normalized_item)
            
            print(f"✅ Found {len(normalized_results)} results from Google Shopping")
            return normalized_results
            
        except Exception as e:
            print(f"❌ Error searching Google Shopping: {e}")
            return []
    
    def _normalize_google_shopping_result(self, item: Dict) -> Optional[Dict]:
        """Normalize Google Shopping result to unified format."""
        try:
            # Extract price
            price_str = item.get("price", "")
            extracted_price = item.get("extracted_price", 0)
            
            # Get source/seller
            source = item.get("source", "Unknown")
            
            # Get rating
            rating = item.get("rating")
            reviews = item.get("reviews")
            
            # Get product details
            title = item.get("title", "")
            link = item.get("link", "")
            thumbnail = item.get("thumbnail", "")
            
            # Delivery info
            delivery = item.get("delivery", "")
            
            return {
                "title": title,
                "price": extracted_price,
                "price_string": price_str,
                "seller": source,
                "url": link,
                "thumbnail": thumbnail,
                "rating": rating,
                "reviews": reviews,
                "delivery": delivery,
                "source": "Google Shopping",
                "in_stock": True  # Assume in stock if listed
            }
            
        except Exception as e:
            print(f"Error normalizing result: {e}")
            return None
    
    def search_all_sources(self, product_info: Dict) -> List[Dict]:
        """
        Search all available sources for product prices.
        
        Args:
            product_info: Parsed product information
            
        Returns:
            Combined list of results from all sources
        """
        all_results = []
        
        # Google Shopping
        google_results = self.search_google_shopping(product_info)
        all_results.extend(google_results)
        
        # Add small delay between API calls
        time.sleep(0.5)
        
        return all_results
    
    def rank_results(self, results: List[Dict], preferences: Dict) -> List[Dict]:
        """
        Rank results based on user preferences.
        
        Args:
            results: List of product results
            preferences: User preferences from parsed data
            
        Returns:
            Ranked list of results
        """
        if not results:
            return []
        
        price_priority = preferences.get("price_priority", "lowest")
        delivery_priority = preferences.get("delivery_priority", False)
        
        # Create scoring function
        def calculate_score(item):
            score = 0
            
            # Price component (higher score for better price)
            price = item.get("price", float('inf'))
            if price > 0:
                # Normalize price (lower is better)
                if price_priority == "lowest":
                    score += 10000 / (price + 1)
            
            # Rating component
            rating = item.get("rating")
            if rating:
                score += float(rating) * 10
            
            # Delivery component
            if delivery_priority:
                delivery = item.get("delivery", "").lower()
                if "free" in delivery:
                    score += 50
                if "fast" in delivery or "express" in delivery:
                    score += 30
            
            return score
        
        # Sort by score
        ranked = sorted(results, key=calculate_score, reverse=True)
        
        return ranked


if __name__ == "__main__":
    # Test the scraper
    scraper = PriceScraper()
    
    test_product = {
        "product": "iPhone 15",
        "brand": "Apple",
        "search_query": "Apple iPhone 15 128GB",
        "region": "India",
        "preferences": {
            "price_priority": "lowest",
            "delivery_priority": True
        }
    }
    
    print("Testing Price Scraper...")
    results = scraper.search_all_sources(test_product)
    
    if results:
        print(f"\n✅ Found {len(results)} results")
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Price: {result['price_string']}")
            print(f"   Seller: {result['seller']}")
            print(f"   Rating: {result.get('rating', 'N/A')}")
    else:
        print("❌ No results found")