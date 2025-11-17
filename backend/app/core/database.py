"""
PostgreSQL database connection configuration.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Check connection before use
    echo=settings.DEBUG   # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency injection for database session.
    
    Yields:
        Session: Database session
        
    Ensures automatic session closure after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
