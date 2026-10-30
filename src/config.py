import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration management."""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    
    REGULATIONS_FILE = os.path.join(DATA_DIR, "sample_regulations.json")
    
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")
    DEBUG = os.environ.get("FLASK_ENV") == "development"
    TESTING = os.environ.get("FLASK_ENV") == "testing"

os.makedirs(Config.STATIC_DIR, exist_ok=True)
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
