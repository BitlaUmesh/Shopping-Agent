"""
Configuration module for the Price Comparison AI system.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    
    # Model Configuration
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Application Settings
    DEFAULT_REGION: str = os.getenv("DEFAULT_REGION", "India")
    DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "INR")
    MAX_RESULTS: int = int(os.getenv("MAX_RESULTS", "10"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        required_keys = [
            ("GEMINI_API_KEY", cls.GEMINI_API_KEY),
            ("SERPAPI_KEY", cls.SERPAPI_KEY),
        ]
        
        missing = [key for key, val in required_keys if not val]
        
        if missing:
            print(f"❌ Missing required configuration: {', '.join(missing)}")
            return False
        
        print("✅ Configuration validated successfully")
        return True


config = Config()