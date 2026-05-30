# backend/database.py
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.config import Config

Base = declarative_base()

class Position(Base):
    __tablename__ = "positions"

    id = Column(String(36), primary_key=True)
    signal_id = Column(String(36), nullable=True)  # None if manual entry
    symbol = Column(String(20), nullable=False)
    market = Column(String(20), nullable=False)  # "crypto", "indian_equity"
    side = Column(String(10), nullable=False)  # "long", "short"
    qty = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    sl = Column(Float, nullable=False)
    tp = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # "OPEN", "CLOSED"
    mode = Column(String(10), nullable=False)  # "paper", "live"
    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)
    exit_reason = Column(String(20), nullable=True)  # "SL", "TP", "manual"
    pnl = Column(Float, nullable=True)

    def calculate_pnl(self, exit_price):
        if self.side == "long":
            return (exit_price - self.entry_price) * self.qty
        else:  # short
            return (self.entry_price - exit_price) * self.qty

class Signal(Base):
    __tablename__ = "signals"

    signal_id = Column(String(36), primary_key=True)
    strategy = Column(String(50), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    confidence = Column(Float, nullable=False)
    emitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    candle_close_time = Column(DateTime, nullable=False)

class Candle(Base):
    __tablename__ = "candles"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    market = Column(String(20), nullable=False)
    timeframe = Column(String(5), nullable=False)
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=False)
    o = Column(Float, nullable=False)
    h = Column(Float, nullable=False)
    l = Column(Float, nullable=False)
    c = Column(Float, nullable=False)
    v = Column(Float, nullable=False)

# Create engine and session
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
