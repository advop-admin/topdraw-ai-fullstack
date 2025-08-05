from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "Topsdraw Blueprint Generator")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    database_url: str = os.getenv("DATABASE_URL")
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))

@lru_cache()
def get_settings() -> Settings:
    return Settings()
