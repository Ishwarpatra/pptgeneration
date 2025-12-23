from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load settings from .env file
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Dependency to get DB session in endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()