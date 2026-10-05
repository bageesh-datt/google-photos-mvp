import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Google Photos AI-Assisted Vague-Memory Retrieval MVP"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Groq Configuration (Support both GROQ_API_KEY and LLM_API_KEY)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY", "")
    GROQ_MODEL: str = os.getenv("LLM_MODEL") or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3.8-27b")
    GROQ_FALLBACK_MODELS: str = os.getenv("GROQ_FALLBACK_MODELS", "")

    
    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    METADATA_PATH: str = (
        os.path.join(BASE_DIR, "backend", "app", "data", "photo_metadata.json")
        if os.path.exists(os.path.join(BASE_DIR, "backend", "app", "data", "photo_metadata.json"))
        else os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "photo_metadata.json"))
    )
    PHOTOS_DIR: str = os.path.join(BASE_DIR, "backend", "app", "data", "photos")
    FRONTEND_PHOTOS_DIR: str = os.path.join(BASE_DIR, "frontend", "public", "photos")
    
    # Scoring Weights (Configurable in one single place)
    WEIGHT_DATE: float = 0.20
    WEIGHT_LOCATION: float = 0.20
    WEIGHT_PEOPLE: float = 0.15
    WEIGHT_EVENT: float = 0.15
    WEIGHT_OBJECTS: float = 0.10
    WEIGHT_OCR: float = 0.10
    WEIGHT_SEMANTIC: float = 0.10
    
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
