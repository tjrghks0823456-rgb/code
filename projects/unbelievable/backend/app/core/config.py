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
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "mock-youtube-api-key")
    
    # Data storage files
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "data")

    # Comma-separated browser origins that can call the API.
    # Keep local development explicit instead of using "*" with credentials.
    CORS_ALLOW_ORIGINS: str = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    )
    
    # Event limits for Free MVP
    MAX_WATCH_EVENTS: int = int(os.getenv("MAX_WATCH_EVENTS", "100"))
    MAX_SEARCH_EVENTS: int = int(os.getenv("MAX_SEARCH_EVENTS", "100"))
    MAX_EVENTS_PER_SOURCE: int = int(os.getenv("MAX_EVENTS_PER_SOURCE", "100"))
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def cors_allow_origins(self) -> list[str]:
        """Return normalized CORS origins from a comma-separated env value."""
        origins = [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",")]
        return [origin for origin in origins if origin]

settings = Settings()

# MVP local test default user ID
DEFAULT_MVP_USER_ID: str = "00000000-0000-0000-0000-000000000001"

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
