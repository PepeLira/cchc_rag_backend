
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from .document_models import Base

DB_PATH = Path("./src/db/parser_database.db")
DB_URL = f"sqlite:///{DB_PATH}"

# Create the engine
engine = create_engine(DB_URL, echo=False, future=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initialize the database (create all tables).
    Typically, you'll rely on Alembic for migrations,
    but you can still use this for a fresh start if needed.
    """
    Base.metadata.create_all(bind=engine)