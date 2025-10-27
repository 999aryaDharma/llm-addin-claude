"""
Configuration settings for Office LLM Add-in Backend
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    GOOGLE_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ENCRYPTION_KEY: str = "change-this-encryption-key"
    
    # LLM Configuration
    LLM_MODEL: str = "gemini-pro"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 8192
    
    # Chunking Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    SUMMARY_BATCH_SIZE: int = 10  # Batch size for summarization
    
    # Chroma Configuration
    CHROMA_DB_PATH: str = "../data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "office_documents"
    
    # Cache Configuration
    CACHE_DB_PATH: str = "../data/cache/summaries.db"
    CACHE_TTL: int = 3600
    MAX_CACHE_SIZE: int = 1000
    
    # Upload Configuration
    UPLOAD_PATH: str = "../data/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".docx", ".xlsx", ".pdf", ".txt"]
    
    # Excel Settings
    MAX_EXCEL_ROWS: int = 10000
    MAX_EXCEL_COLS: int = 100
    
    # Word Settings
    MAX_WORD_CHARS: int = 100000
    
    # Server Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_ENV: str = "development"
    CORS_ORIGINS: List[str] = ["https://localhost:3000", "http://localhost:3000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "../data/logs"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

    @property
    def cache_path(self) -> Path:
        """Get absolute path for cache DB"""
        return Path(__file__).parent.parent / self.CACHE_DB_PATH

    @property
    def log_path(self) -> Path:
        """Get absolute path for logs"""
        return Path(__file__).parent.parent / self.LOG_PATH


# Initialize settings
settings = Settings()


# Create directories if they don't exist
def ensure_directories():
    """Ensure all required directories exist"""
    dirs = [
        Path(settings.CHROMA_DB_PATH),
        Path(settings.UPLOAD_PATH),
        Path(settings.CACHE_DB_PATH).parent,
        Path(settings.LOG_PATH)
    ]
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)


ensure_directories()