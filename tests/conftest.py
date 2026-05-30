# tests/conftest.py
import pytest
import tempfile
import os
from backend.database import Base, SessionLocal, engine


@pytest.fixture(scope="function")
def setup_db():
    """Create a fresh in-memory database for each test"""
    # Create all tables
    Base.metadata.create_all(engine)

    yield

    # Cleanup: drop all tables
    Base.metadata.drop_all(engine)
