"""
AI Agents Module
Implements Shopping Assistant and Research Assistant with tool calling.
"""

import google.generativeai as genai
from typing import Dict, List, Optional
from langchain_community.tools import DuckDuckGoSearchRun
from .config import config
from .vector_db import VectorDatabase


class ShoppingAssistant:
    """Context-aware shopping assistant for quick queries."""
    
    def __init__(self, context: Dict = None):
        """
        Initialize shopping assistant.
        
        Args:
            context: Conversation context including recommendations
        """
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        self.context = context or {}
        self.conversation_history = []
    
    def chat(self, user_message: str) -> str:
        """
        Chat with the shopping assistant.
        
        Args:
            user_message: User's message
            
        Returns:
            Assistant's response
        """
        # Build context-aware prompt
        context_info = self._build_context()
        
        prompt = f"""
You are a helpful shopping assistant. You have access to the following context about the user's product search:

{context_info}

Conversation History:
{self._format_history()}

User: {user_message}

Provide a helpful, concise response based on the context. If the user asks about specific products in the results, reference them. Be friendly and informative.
"""
        
        try:
            response = self.model.generate_content(prompt)
            assistant_response = response.text
            
            # Update history
            self.conversation_history.append({
                "role": "user",
                "message": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "message": assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            print(f"Error in shopping assistant: {e}")
            return "I apologize, but I encountered an error. Please try again."
    
    def _build_context(self) -> str:
        """Build context string from stored data."""
        if not self.context:
            return "No product search has been performed yet."
        
        parts = []
        
        # Add product info
        if "product_info" in self.context:
            info = self.context["product_info"]
            parts.append(f"Searching for: {info.get('search_query', 'N/A')}")
        
        # Add recommendation
        if "recommendation" in self.context:
            rec = self.context["recommendation"]
            if rec.get("status") == "success":
                parts.append(f"\nTop Recommendation: {rec.get('analysis', '')}")
                
                if "products" in rec and rec["products"]:
                    parts.append("\nTop Products:")
                    for i, prod in enumerate(rec["products"][:3], 1):
                        parts.append(
                            f"{i}. {prod.get('title')} - "
                            f"{prod.get('price_string')} from {prod.get('seller')}"
                        )
        
        return "\n".join(parts) if parts else "No context available."
    
    def _format_history(self) -> str:
        """Format conversation history."""
        if not self.conversation_history:
            return "No previous conversation."
        
        formatted = []
        for entry in self.conversation_history[-4:]:  # Last 4 messages
            role = entry["role"].capitalize()
            message = entry["message"][:200]  # Truncate long messages
            formatted.append(f"{role}: {message}")
        
        return "\n".join(formatted)
    
    def update_context(self, context: Dict) -> None:
        """Update the conversation context."""
        self.context.update(context)


class ResearchAssistant:
    """Advanced research assistant with tool calling capabilities."""
    
    def __init__(self, vector_db: VectorDatabase = None):
        """
        Initialize research assistant.
        
        Args:
            vector_db: Vector database for RAG
        """
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        self.vector_db = vector_db or VectorDatabase()
        self.search_tool = DuckDuckGoSearchRun()
        self.conversation_history = []
    
    def chat(self, user_message: str, use_tools: bool = True) -> str:
        """
        Chat with research assistant, potentially using tools.
        
        Args:
            user_message: User's message
            use_tools: Whether to use external tools
            
        Returns:
            Assistant's response
        """
        # Determine if tools are needed
        needs_search = self._needs_web_search(user_message)
        needs_rag = self._needs_vector_search(user_message)
        
        additional_context = ""
        
        # Use tools if needed and allowed
        if use_tools:
            if needs_search:
                search_results = self._web_search(user_message)
                additional_context += f"\n\nWeb Search Results:\n{search_results}"
            
            if needs_rag:
                similar_products = self._vector_search(user_message)
                additional_context += f"\n\nSimilar Products:\n{similar_products}"
        
        # Generate response
        prompt = f"""
You are an advanced research assistant specializing in product analysis and comparison.

Conversation History:
{self._format_history()}

Additional Context (from tools):
{additional_context}

User: {user_message}

Provide a comprehensive, well-researched response. Use the context from tools when available. Be analytical and objective.
"""
        
        try:
            response = self.model.generate_content(prompt)
            assistant_response = response.text
            
            # Update history
            self.conversation_history.append({
                "role": "user",
                "message": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "message": assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            print(f"Error in research assistant: {e}")
            return "I apologize, but I encountered an error during research. Please try again."
    
    def _needs_web_search(self, message: str) -> bool:
        """Determine if web search is needed."""
        search_keywords = [
            "compare", "vs", "versus", "review", "latest", "news",
            "price history", "trends", "alternative", "similar"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in search_keywords)
    
    def _needs_vector_search(self, message: str) -> bool:
        """Determine if vector search is needed."""
        rag_keywords = [
            "similar", "like", "alternative", "comparable",
            "other options", "different", "related"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in rag_keywords)
    
    def _web_search(self, query: str) -> str:
        """Perform web search."""
        try:
            print(f"🔍 Performing web search for: {query}")
            results = self.search_tool.run(query)
            return results[:1000]  # Limit length
        except Exception as e:
            print(f"Web search error: {e}")
            return "Web search unavailable."
    
    def _vector_search(self, query: str) -> str:
        """Perform vector similarity search."""
        try:
            print(f"🔍 Performing vector search for: {query}")
            results = self.vector_db.search_similar_products(query, n_results=3)
            
            if not results:
                return "No similar products found in database."
            
            formatted = []
            for result in results:
                formatted.append(
                    f"- {result.get('title')} "
                    f"(Price: {result.get('price')}, "
                    f"Rating: {result.get('rating')}, "
                    f"Similarity: {result.get('similarity_score', 0):.2f})"
                )
            
            return "\n".join(formatted)
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return "Vector search unavailable."
    
    def _format_history(self) -> str:
        """Format conversation history."""
        if not self.conversation_history:
            return "No previous conversation."
        
        formatted = []
        for entry in self.conversation_history[-4:]:  # Last 4 messages
            role = entry["role"].capitalize()
            message = entry["message"][:200]  # Truncate long messages
            formatted.append(f"{role}: {message}")
        
        return "\n".join(formatted)


if __name__ == "__main__":
    # Test Shopping Assistant
    print("Testing Shopping Assistant...")
    context = {
        "product_info": {
            "search_query": "iPhone 15 128GB"
        },
        "recommendation": {
            "status": "success",
            "analysis": "Best deals found on Amazon and Flipkart",
            "products": [
                {
                    "title": "iPhone 15 128GB",
                    "price_string": "₹79,900",
                    "seller": "Amazon"
                }
            ]
        }
    }
    
    assistant = ShoppingAssistant(context)
    response = assistant.chat("Is the Amazon seller reliable?")
    print(f"\nResponse: {response}")
    
    # Test Research Assistant
    print("\n\nTesting Research Assistant...")
    research = ResearchAssistant()
    response = research.chat("Compare iPhone 15 with Samsung S23", use_tools=False)
    print(f"\nResponse: {response}")