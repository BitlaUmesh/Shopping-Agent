import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    DEFAULT_REGION = "India"
    DEFAULT_CURRENCY = "INR"
    MAX_RESULTS = 10

    @classmethod
    def validate(cls) -> bool:
        if not cls.GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY missing")
            return False
        if not cls.SERPAPI_KEY:
            print("❌ SERPAPI_KEY missing")
            return False
        return True

config = Config()
