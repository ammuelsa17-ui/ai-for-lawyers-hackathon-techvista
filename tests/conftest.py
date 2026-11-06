import os
import tempfile
import sqlite3
import pytest
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db, init_db
from app.db.models import MatterModel


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@pytest.fixture(scope="function")
def temp_db_path():
    """Create an isolated temporary SQLite database file for each test."""
    temp_dir = tempfile.TemporaryDirectory()
    db_file = Path(temp_dir.name) / "test_casepilot.db"
    
    # Run canonical schema.sql
    init_db(db_path=str(db_file))
    
    yield str(db_file)
    temp_dir.cleanup()


@pytest.fixture(scope="function")
def db_session(temp_db_path):
    """Provide a SQLAlchemy session connected to the temporary SQLite DB with foreign keys ON."""
    engine = create_engine(
        f"sqlite:///{temp_db_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(temp_db_path, db_session):
    """Provide a TestClient with get_db overridden to point to the isolated temp DB."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
