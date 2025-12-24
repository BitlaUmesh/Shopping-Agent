from typing import Dict, List, Optional, Tuple
from .config import config
from .parser import ProductParser
from .scraper import PriceScraper
from .vector_db import VectorDatabase
from .recommender import ProductRecommender
from .agents import ShoppingAssistant, ResearchAssistant


class PriceComparisonApp:
    def __init__(self):
        if not config.validate():
            raise ValueError("Invalid configuration. Check .env")

        self.parser = ProductParser()
        self.scraper = PriceScraper()
        self.vector_db = VectorDatabase()
        self.recommender = ProductRecommender()

        self.shopping_assistant = None
        self.research_assistant = None

    def process_query(
        self,
        user_query: str,
        progress_callback=None
    ) -> Tuple[Dict, Dict, List[Dict]]:

        def update(step, pct):
            if progress_callback:
                progress_callback(step, pct)

        # 1️⃣ Parse user query using AI
        update("Understanding your request…", 10)
        product_info = self.parser.parse_query(user_query)

        # 2️⃣ REAL SEARCH — GOOGLE SHOPPING (Amazon, Flipkart, etc.)
        update("Searching shopping websites…", 30)
        search_results = self.scraper.search_all_sources(product_info)

        if not search_results:
            return product_info, {
                "status": "no_results",
                "analysis": "No products found online."
            }, []

        # 3️⃣ Rank results
        update("Ranking best deals…", 50)
        ranked_results = self.scraper.rank_results(
            search_results,
            product_info.get("preferences", {})
        )

        # 4️⃣ Store in vector DB (for assistant & research)
        update("Analyzing products…", 70)
        self.vector_db.add_products(ranked_results)

        # 5️⃣ AI recommendation on REAL DATA
        update("Generating AI recommendation…", 85)
        recommendation = self.recommender.generate_recommendation(
            product_info,
            ranked_results,
            top_n=5
        )

        # 6️⃣ Init assistants
        update("Finalizing results…", 100)
        context = {
            "product_info": product_info,
            "recommendation": recommendation
        }

        self.shopping_assistant = ShoppingAssistant(context)
        self.research_assistant = ResearchAssistant(self.vector_db)

        return product_info, recommendation, ranked_results
