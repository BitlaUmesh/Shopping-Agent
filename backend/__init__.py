"""
Backend Package
AI-Driven Product Price Comparison System
"""

from .app import PriceComparisonApp
from .config import config
from .parser import ProductParser
from .scraper import PriceScraper
from .vector_db import VectorDatabase
from .recommender import ProductRecommender
from .agents import ShoppingAssistant, ResearchAssistant

__all__ = [
    'PriceComparisonApp',
    'config',
    'ProductParser',
    'PriceScraper',
    'VectorDatabase',
    'ProductRecommender',
    'ShoppingAssistant',
    'ResearchAssistant'
]

__version__ = '1.0.0'