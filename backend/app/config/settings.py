"""
Application settings and configuration
Updated to support both local ChromaDB container and cloud deployment
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Topsdraw Compass"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Gemini API Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = "gemini-1.5-pro"
    
    # Chroma DB Configuration - Supports both container and cloud
    chroma_host: str = os.getenv("CHROMA_HOST", "chroma")  # Default to container service name
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
    chroma_api_key: Optional[str] = os.getenv("CHROMA_API_KEY")  # Only needed for cloud
    chroma_collection_name: str = "topsdraw_compass_projects"
    

    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # Scraping Configuration
    request_timeout: int = 30
    max_retries: int = 3
    user_agent: str = "Topsdraw-Compass/1.0"
    
    @property
    def get_database_url(self) -> str:
        """Get database URL - prioritize DATABASE_URL, fallback to individual params"""
        if self.database_url:
            return self.database_url
        
        # Construct from individual parameters
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def is_chroma_cloud(self) -> bool:
        """Check if using ChromaDB cloud or local container"""
        return bool(self.chroma_api_key)
    
    @property
    def chroma_connection_info(self) -> dict:
        """Get ChromaDB connection information"""
        if self.is_chroma_cloud:
            return {
                "type": "cloud",
                "host": self.chroma_host,
                "port": self.chroma_port,
                "headers": {"Authorization": f"Bearer {self.chroma_api_key}"}
            }
        else:
            return {
                "type": "container",
                "host": self.chroma_host,
                "port": self.chroma_port,
                "headers": None
            }
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    """Get application settings"""
    return Settings() 