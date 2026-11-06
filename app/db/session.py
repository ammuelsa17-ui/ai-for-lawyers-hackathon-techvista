import os
import sqlite3
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

Base = declarative_base()

# Enable SQLite foreign key constraints on every connection
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_sqlite_url(db_path: str) -> str:
    path_obj = Path(db_path).resolve()
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path_obj}"


engine = create_engine(
    get_sqlite_url(settings.database_path),
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(db_path: str | None = None, schema_path: str | None = None) -> None:
    """Execute canonical schema.sql using raw sqlite3 executescript."""
    target_path = Path(db_path if db_path else settings.database_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if schema_path is None:
        schema_file = Path(__file__).parent / "schema.sql"
    else:
        schema_file = Path(schema_path)

    with open(schema_file, "r", encoding="utf-8") as f:
        schema_ddl = f.read()

    conn = sqlite3.connect(str(target_path))
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(schema_ddl)
        conn.commit()
    finally:
        conn.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
