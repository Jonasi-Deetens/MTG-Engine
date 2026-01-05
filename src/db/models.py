from sqlalchemy import Column, String, JSON, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Axis1CardModel(Base):
    __tablename__ = "axis1_cards"

    card_id = Column(String, primary_key=True)
    oracle_id = Column(String, index=True)
    set_code = Column(String, index=True)
    collector_number = Column(String)
    layout = Column(String)
    name = Column(String, index=True)
    lang = Column(String)
    axis1_json = Column(JSON)  # store full Axis1Card dict

class Axis2TestCard(Base):
    __tablename__ = "axis2_test_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    axis2_json = Column(JSON, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to sessions (optional, for database-backed sessions)
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    """
    Optional: Database-backed session storage.
    Currently using in-memory sessions, but this model allows
    switching to database-backed sessions for production.
    """
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)  # session_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Relationship to user
    user = relationship("User", back_populates="sessions")
