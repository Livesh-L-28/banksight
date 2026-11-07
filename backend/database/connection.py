"""
BankSight Relational Database Connection & Session Management
Supports both PostgreSQL (Production / Docker / CI) and SQLite (Local Development / Testing).
"""

import os
from pathlib import Path
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine

# Load environment variables
load_dotenv()

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "banksight.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# If SQLite, ensure the parent directory exists
if DATABASE_URL.startswith("sqlite"):
    db_file_path = DATABASE_URL.replace("sqlite:///", "")
    if db_file_path and not db_file_path.startswith(":memory:"):
        Path(db_file_path).parent.mkdir(parents=True, exist_ok=True)

# Engine configuration
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Session:
    """Returns a new SQLAlchemy Session."""
    return SessionLocal()


@contextmanager
def get_db_context():
    """Context manager for safe transactional database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

