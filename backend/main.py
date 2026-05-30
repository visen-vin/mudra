# backend/main.py
import asyncio
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import redis.asyncio as redis

from backend.config import Config
from backend.database import init_db
from backend.api.routes import router
from backend.services.data_ingestion import DataIngestionService
from backend.feeds.binance import BinanceAdapter
from backend.feeds.zerodha import ZerodhaAdapter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing Mudra System...")
    init_db()
    
    # Initialize Adapters
    binance = BinanceAdapter()
    zerodha = ZerodhaAdapter()
    if os.getenv("ZERODHA_ACCESS_TOKEN"):
        zerodha.access_token = os.getenv("ZERODHA_ACCESS_TOKEN")
    
    # Initialize Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(redis_url, decode_responses=True)
    
    # Initialize and Start Data Ingestion Service
    ingestion_service = DataIngestionService(
        redis_client=redis_client,
        binance_adapter=binance,
        zerodha_adapter=zerodha
    )
    
    # Start ingestion in the background
    ingestion_task = asyncio.create_task(ingestion_service.run())
    
    # Store instances in app state for access in routes if needed
    app.state.binance = binance
    app.state.zerodha = zerodha
    app.state.redis = redis_client
    app.state.ingestion_service = ingestion_service
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down Mudra System...")
    ingestion_task.cancel()
    await binance.disconnect()
    await redis_client.close()

app = FastAPI(title="Mudra Trading", version="0.1.0", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Include API routes
app.include_router(router)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
