# backend/services/signal_service.py
from backend.database import Signal, SessionLocal
from backend.schemas import SignalCreate
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class SignalService:
    """Manages trading signals from strategies"""
    
    @staticmethod
    def create_signal(strategy: str, symbol: str, side: str, confidence: float, candle_close_time: datetime) -> Signal:
        """Persist signal to database"""
        db = SessionLocal()
        try:
            signal = Signal(
                signal_id=str(uuid.uuid4()),
                strategy=strategy,
                symbol=symbol,
                side=side,
                confidence=confidence,
                emitted_at=datetime.utcnow(),
                candle_close_time=candle_close_time
            )
            db.add(signal)
            db.commit()
            db.refresh(signal)
            
            logger.info(f"Signal created: {signal.signal_id} {strategy} {symbol} {side} @ {confidence}")
            return signal
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating signal: {str(e)}")
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_signals(limit: int = 100, offset: int = 0):
        """Retrieve recent signals"""
        db = SessionLocal()
        try:
            return db.query(Signal).order_by(Signal.emitted_at.desc()) \
                .offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching signals: {str(e)}")
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_signals_by_strategy(strategy: str, limit: int = 100):
        """Get signals from specific strategy"""
        db = SessionLocal()
        try:
            return db.query(Signal).filter(Signal.strategy == strategy) \
                .order_by(Signal.emitted_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching signals by strategy: {str(e)}")
            raise e
        finally:
            db.close()
