from sqlalchemy import Column, String, JSON, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint
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

class Keyword(Base):
    """MTG keyword abilities with their configurable parameters."""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    
    # Parameter flags
    has_cost = Column(Boolean, default=False)
    has_mana_cost = Column(Boolean, default=False)
    has_number = Column(Boolean, default=False)
    has_life_cost = Column(Boolean, default=False)
    has_sacrifice_cost = Column(Boolean, default=False)
    has_discard_cost = Column(Boolean, default=False)
    
    # Parameter type identifiers
    cost_type = Column(String)  # "mana", "life", "sacrifice", "discard", etc.
    number_type = Column(String)  # "annihilator", "bloodthirst", "ward", etc.
    
    # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CardAbilityGraph(Base):
    """Stores ability graphs built for specific cards from Skyfall."""
    __tablename__ = "card_ability_graphs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, nullable=False, index=True)  # Reference to Skyfall card_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Store the full ability graph JSON
    ability_graph_json = Column(JSON, nullable=False)  # Full AbilityGraph structure
    
    # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", backref="card_ability_graphs")
    
    # Unique constraint: one graph per card per user
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class UserFavorite(Base):
    """User's favorite cards."""
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    card_id = Column(String, nullable=False, index=True)  # Reference to Axis1CardModel.card_id
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", backref="favorites")
    
    # Unique constraint: one favorite per card per user
    __table_args__ = (
        UniqueConstraint('user_id', 'card_id', name='uq_user_favorite'),
        {"sqlite_autoincrement": True},
    )


class Collection(Base):
    """User-created card collections."""
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", backref="collections")
    
    # Relationship to collection items
    items = relationship("CollectionItem", back_populates="collection", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class CollectionItem(Base):
    """Cards in a collection."""
    __tablename__ = "collection_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False, index=True)
    card_id = Column(String, nullable=False, index=True)  # Reference to Axis1CardModel.card_id
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to collection
    collection = relationship("Collection", back_populates="items")
    
    # Unique constraint: one card per collection
    __table_args__ = (
        UniqueConstraint('collection_id', 'card_id', name='uq_collection_item'),
        {"sqlite_autoincrement": True},
    )
