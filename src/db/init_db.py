# src/db/init_db.py

"""
Initialize database tables.
Run this once to create all tables defined in models.py
"""

from db.connection import engine
from db.models import Base

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()

