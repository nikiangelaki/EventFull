import os
from dotenv import load_dotenv

# Φόρτωσε τις μεταβλητές από το .env αρχείο
load_dotenv()

class Settings:
    """
    Κεντρική κλάση ρυθμίσεων.
    Διαβάζει τιμές από environment variables.
    """
    
    # Database settings
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "EventFull")
    
    # Δημιουργία του DATABASE_URL για SQLAlchemy
    # Μορφή: mysql+pymysql://user:password@host:port/database
    DATABASE_URL: str = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Server & Security settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret")
    # χρόνο λήξης του JWT Token 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Δημιουργία instance
settings = Settings()