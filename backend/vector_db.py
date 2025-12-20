"""
Vector Database Module
Manages ChromaDB for product embeddings and similarity search.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import json
from .config import config


class VectorDatabase:
    """Vector database for product information and RAG."""
    
    def __init__(self):
        """Initialize ChromaDB and embeddings."""
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="products",
            metadata={"description": "Product information for price comparison"}
        )
        
        print(f"✅ Vector database initialized. Collection size: {self.collection.count()}")
    
    def add_products(self, products: List[Dict]) -> None:
        """
        Add products to the vector database.
        
        Args:
            products: List of product dictionaries
        """
        if not products:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for i, product in enumerate(products):
            # Create searchable text
            doc_text = self._create_document_text(product)
            documents.append(doc_text)
            
            # Store metadata
            metadata = {
                "title": product.get("title", "")[:500],  # Limit length
                "price": product.get("price", 0),
                "seller": product.get("seller", "")[:100],
                "rating": product.get("rating", 0) or 0,
                "url": product.get("url", "")[:500],
                "source": product.get("source", "")
            }
            metadatas.append(metadata)
            
            # Generate unique ID
            product_id = f"product_{int(time.time() * 1000)}_{i}"
            ids.append(product_id)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(products)} products to vector database")
    
    def search_similar_products(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search for similar products using semantic search.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar products
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        similar_products = []
        if results["metadatas"]:
            for metadata, document, distance in zip(
                results["metadatas"][0],
                results["documents"][0],
                results["distances"][0]
            ):
                product = {
                    **metadata,
                    "document": document,
                    "similarity_score": 1 - distance  # Convert distance to similarity
                }
                similar_products.append(product)
        
        return similar_products
    
    def _create_document_text(self, product: Dict) -> str:
        """Create searchable text from product data."""
        parts = [
            f"Product: {product.get('title', '')}",
            f"Seller: {product.get('seller', '')}",
            f"Price: {product.get('price_string', '')}",
            f"Rating: {product.get('rating', 'N/A')}",
        ]
        
        if product.get("delivery"):
            parts.append(f"Delivery: {product['delivery']}")
        
        return " | ".join(parts)
    
    def clear_database(self) -> None:
        """Clear all data from the database."""
        self.client.delete_collection("products")
        self.collection = self.client.get_or_create_collection(
            name="products",
            metadata={"description": "Product information for price comparison"}
        )
        print("✅ Vector database cleared")


import time

if __name__ == "__main__":
    # Test the vector database
    db = VectorDatabase()
    
    # Test products
    test_products = [
        {
            "title": "Apple iPhone 15 128GB Blue",
            "price": 79900,
            "price_string": "₹79,900",
            "seller": "Amazon",
            "rating": 4.5,
            "url": "https://example.com",
            "source": "Google Shopping"
        },
        {
            "title": "Samsung Galaxy S23 128GB Black",
            "price": 74999,
            "price_string": "₹74,999",
            "seller": "Flipkart",
            "rating": 4.6,
            "url": "https://example.com",
            "source": "Google Shopping"
        }
    ]
    
    print("\nAdding test products...")
    db.add_products(test_products)
    
    print("\nSearching for similar products...")
    results = db.search_similar_products("iPhone", n_results=2)
    
    print(f"\nFound {len(results)} similar products:")
    for result in results:
        print(f"- {result['title']} (Similarity: {result['similarity_score']:.2f})")