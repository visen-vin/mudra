# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mudra.db")
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
    ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY", "")
    ZERODHA_SESSION_TOKEN = os.getenv("ZERODHA_SESSION_TOKEN", "")

    # Trading defaults
    DEFAULT_MODE = os.getenv("DEFAULT_MODE", "paper")
    DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "15m")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
