import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve the database URL; fallback to SQLite for safety
DATABASE_URL = os.getenv('DB_URL') or os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Default to a local SQLite database (relative to project root)
    DATABASE_URL = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "quiz.db"))

# Create the engine; enable future flag for SQLAlchemy 2.0 style if desired
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Scoped session for thread‑local usage in Flask
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """Dependency helper to provide a DB session.
    Usage::
        with get_db() as db:
            # use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
