import json
import logging
from typing import List, Dict, Optional
import redis.asyncio as redis
from sqlalchemy.orm import Session
from backend.database import SessionLocal, WatchlistSymbol

logger = logging.getLogger(__name__)

class WatchlistManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.redis_key = "watchlist:active"

    async def sync_redis_from_db(self):
        """Restore Redis watchlist from database on startup"""
        try:
            db = SessionLocal()
            symbols = db.query(WatchlistSymbol).all()
            symbol_list = [s.symbol for s in symbols]
            await self.redis.set(self.redis_key, json.dumps(symbol_list))
            logger.info(f"Watchlist synced: {len(symbol_list)} symbols")
            db.close()
        except Exception as e:
            logger.error(f"Error syncing watchlist: {e}")

    async def get_active_watchlist(self) -> List[str]:
        """Return list of active symbols from Redis"""
        data = await self.redis.get(self.redis_key)
        return json.loads(data) if data else []

    async def add_symbol(self, symbol: str, market: str):
        """Add symbol to watchlist (DB + Redis)"""
        db = SessionLocal()
        try:
            # Add to DB if not exists
            existing = db.query(WatchlistSymbol).filter(WatchlistSymbol.symbol == symbol).first()
            if not existing:
                new_s = WatchlistSymbol(symbol=symbol, market=market)
                db.add(new_s)
                db.commit()
            
            # Update Redis
            current = await self.get_active_watchlist()
            if symbol not in current:
                current.append(symbol)
                await self.redis.set(self.redis_key, json.dumps(current))
            
            return current
        finally:
            db.close()

    async def remove_symbol(self, symbol: str):
        """Remove symbol from watchlist (DB + Redis)"""
        db = SessionLocal()
        try:
            # Remove from DB
            db.query(WatchlistSymbol).filter(WatchlistSymbol.symbol == symbol).delete()
            db.commit()
            
            # Update Redis
            current = await self.get_active_watchlist()
            if symbol in current:
                current.remove(symbol)
                await self.redis.set(self.redis_key, json.dumps(current))
            
            return current
        finally:
            db.close()
