"""
Main Application Module
Orchestrates the entire price comparison workflow.
"""

from typing import Dict, List, Optional, Tuple
from .config import config
from .parser import ProductParser
from .scraper import PriceScraper
from .vector_db import VectorDatabase
from .recommender import ProductRecommender
from .agents import ShoppingAssistant, ResearchAssistant


class PriceComparisonApp:
    """Main application orchestrator."""
    
    def __init__(self):
        """Initialize all components."""
        print("🚀 Initializing Price Comparison AI...")
        
        # Validate configuration
        if not config.validate():
            raise ValueError("Invalid configuration. Please check your .env file.")
        
        # Initialize components
        self.parser = ProductParser()
        self.scraper = PriceScraper()
        self.vector_db = VectorDatabase()
        self.recommender = ProductRecommender()
        
        # Initialize agents (will be created per session)
        self.shopping_assistant = None
        self.research_assistant = None
        
        print("✅ Application initialized successfully!")
    
    def process_query(
        self,
        user_query: str,
        progress_callback: Optional[callable] = None
    ) -> Tuple[Dict, Dict, List[Dict]]:
        """
        Process a user query end-to-end.
        
        Args:
            user_query: Natural language product query
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (product_info, recommendation, all_results)
        """
        def update_progress(step: str, progress: int):
            if progress_callback:
                progress_callback(step, progress)
        
        # Step 1: Parse query
        update_progress("Parsing your request...", 10)
        product_info = self.parser.parse_query(user_query)
        print(f"📝 Parsed product: {product_info.get('search_query')}")
        
        # Step 2: Search for products
        update_progress("Searching for products...", 30)
        search_results = self.scraper.search_all_sources(product_info)
        
        if not search_results:
            update_progress("No results found", 100)
            return product_info, {"status": "no_results"}, []
        
        print(f"🔍 Found {len(search_results)} products")
        
        # Step 3: Rank results
        update_progress("Ranking results...", 50)
        preferences = product_info.get("preferences", {})
        ranked_results = self.scraper.rank_results(search_results, preferences)
        
        # Step 4: Store in vector database
        update_progress("Storing product data...", 60)
        self.vector_db.add_products(ranked_results)
        
        # Step 5: Generate recommendation
        update_progress("Generating recommendations...", 80)
        recommendation = self.recommender.generate_recommendation(
            product_info,
            ranked_results,
            top_n=5
        )
        
        # Step 6: Initialize agents with context
        update_progress("Preparing assistants...", 90)
        self._initialize_agents(product_info, recommendation)
        
        update_progress("Complete!", 100)
        
        return product_info, recommendation, ranked_results
    
    def _initialize_agents(self, product_info: Dict, recommendation: Dict) -> None:
        """Initialize AI agents with context."""
        context = {
            "product_info": product_info,
            "recommendation": recommendation
        }
        
        self.shopping_assistant = ShoppingAssistant(context)
        self.research_assistant = ResearchAssistant(self.vector_db)
    
    def chat_with_shopping_assistant(self, message: str) -> str:
        """
        Chat with the shopping assistant.
        
        Args:
            message: User message
            
        Returns:
            Assistant response
        """
        if not self.shopping_assistant:
            return "Please perform a product search first."
        
        return self.shopping_assistant.chat(message)
    
    def chat_with_research_assistant(self, message: str) -> str:
        """
        Chat with the research assistant.
        
        Args:
            message: User message
            
        Returns:
            Assistant response
        """
        if not self.research_assistant:
            self.research_assistant = ResearchAssistant(self.vector_db)
        
        return self.research_assistant.chat(message)
    
    def get_product_details(self, product_index: int, results: List[Dict]) -> Optional[Dict]:
        """
        Get detailed information about a specific product.
        
        Args:
            product_index: Index of product in results
            results: List of product results
            
        Returns:
            Product details or None
        """
        if 0 <= product_index < len(results):
            return results[product_index]
        return None
    
    def clear_session(self) -> None:
        """Clear current session data."""
        self.shopping_assistant = None
        self.research_assistant = None
        # Note: We don't clear vector_db as it can be useful across sessions


if __name__ == "__main__":
    # Test the complete application
    print("=" * 60)
    print("Testing Price Comparison AI Application")
    print("=" * 60)
    
    try:
        app = PriceComparisonApp()
        
        # Test query
        test_query = "Find the cheapest iPhone 15 128GB in India"
        print(f"\n📱 Query: {test_query}\n")
        
        # Process query
        product_info, recommendation, results = app.process_query(test_query)
        
        # Display results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print(f"\n📦 Product: {product_info.get('search_query')}")
        print(f"🌍 Region: {product_info.get('region')}")
        
        if recommendation.get("status") == "success":
            print(f"\n💡 Analysis: {recommendation.get('analysis')}")
            
            products = recommendation.get("products", [])
            if products:
                print(f"\n🏆 Top {len(products)} Recommendations:\n")
                for i, prod in enumerate(products, 1):
                    print(f"{i}. {prod.get('title')}")
                    print(f"   💰 {prod.get('price_string')}")
                    print(f"   🏪 {prod.get('seller')}")
                    print(f"   ⭐ {prod.get('rating', 'N/A')}")
                    print(f"   🔗 {prod.get('url')[:50]}...")
                    print()
        
        # Test shopping assistant
        print("\n" + "=" * 60)
        print("SHOPPING ASSISTANT TEST")
        print("=" * 60)
        
        response = app.chat_with_shopping_assistant("Is the top seller reliable?")
        print(f"\n🤖 Assistant: {response}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()