import time
from typing import Dict, List, Optional
from serpapi import GoogleSearch
from .config import config


class PriceScraper:
    def __init__(self):
        self.api_key = config.SERPAPI_KEY

    def search_google_shopping(self, product_info: Dict) -> List[Dict]:
        query = product_info.get("search_query", "")
        region = product_info.get("region", "India")

        # 🔥 FORCE INDIA + INR
        params = {
            "engine": "google_shopping",
            "q": query,
            "location": "India",
            "google_domain": "google.co.in",
            "gl": "in",
            "hl": "en",
            "currency": "INR",
            "api_key": self.api_key,
            "num": config.MAX_RESULTS
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            items = results.get("shopping_results", [])

            parsed = []
            for item in items:
                parsed_item = self._normalize_result(item)
                if parsed_item:
                    parsed.append(parsed_item)

            return parsed

        except Exception as e:
            print("❌ Google Shopping error:", e)
            return []

    def _normalize_result(self, item: Dict) -> Optional[Dict]:
        try:
            return {
                "title": item.get("title"),
                "price": item.get("extracted_price"),
                "price_string": item.get("price", "₹ N/A"),
                "seller": item.get("source", "Unknown"),
                "rating": item.get("rating"),
                "reviews": item.get("reviews"),
                "url": item.get("link"),
                "thumbnail": item.get("thumbnail"),
                "delivery": item.get("delivery"),
                "source": "Google Shopping",
                "currency": "INR",
                "in_stock": True
            }
        except Exception:
            return None

    def search_all_sources(self, product_info: Dict) -> List[Dict]:
        return self.search_google_shopping(product_info)

    def rank_results(self, results: List[Dict], preferences: Dict) -> List[Dict]:
        return sorted(
            results,
            key=lambda x: x.get("price", float("inf"))
        )
