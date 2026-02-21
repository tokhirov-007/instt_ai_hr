import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (one level up from /app)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    SPACY_MODEL: str = "en_core_web_sm"
    TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    
    # SMTP Settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "") # App Password for Gmail
    
    # CORS Settings
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

settings = Settings()
