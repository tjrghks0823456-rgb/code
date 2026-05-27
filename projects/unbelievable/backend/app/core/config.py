import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "언블리버블 (Unbelievable)"
    VERSION: str = "1.0.0-MVP"
    API_V1_STR: str = "/api/v1"
    
    # Database / Supabase Credentials (default placeholders for prototype)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-supabase-url.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "your-supabase-anon-key")
    
    # API Keys
    GOOGLE_LANGUAGE_API_KEY: str = os.getenv("GOOGLE_LANGUAGE_API_KEY", "mock-nl-api-key")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "mock-gemini-api-key")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "mock-youtube-api-key")
    
    # Data storage files
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "data")
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
