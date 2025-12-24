from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class VectorDatabase:
    def __init__(self):
        # ✅ Force CPU (already fixed)
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cpu"
        )

        # ✅ Explicit tenant + database (FIXES default_tenant ERROR)
        self.client = chromadb.Client(
            Settings(
                persist_directory="./chroma_db",
                anonymized_telemetry=False
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="products"
        )

    def add_products(self, products: List[Dict]):
        if not products:
            return

        documents = []
        ids = []

        for i, product in enumerate(products):
            documents.append(product.get("title", ""))
            ids.append(f"product_{i}")

        embeddings = self.embedding_model.encode(
            documents,
            convert_to_numpy=True
        ).tolist()

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids
        )

    def search_similar_products(self, query: str, n_results: int = 3):
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).tolist()

        return self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
