"""Configuration management for the Flight Agent."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Amadeus
    AMADEUS_CLIENT_ID: str = os.getenv("AMADEUS_CLIENT_ID", "")
    AMADEUS_CLIENT_SECRET: str = os.getenv("AMADEUS_CLIENT_SECRET", "")
    AMADEUS_HOSTNAME: str = os.getenv("AMADEUS_HOSTNAME", "test")
    
    # Agent settings
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate that required configuration is present."""
        errors = []
        
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is not set")
        
        if not cls.AMADEUS_CLIENT_ID:
            errors.append("AMADEUS_CLIENT_ID is not set")
            
        if not cls.AMADEUS_CLIENT_SECRET:
            errors.append("AMADEUS_CLIENT_SECRET is not set")
            
        return errors


config = Config()
