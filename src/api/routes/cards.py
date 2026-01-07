# src/api/routes/cards.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List

from db.connection import SessionLocal
from db.models import Axis1CardModel
from db.repository import Axis1Repository
from scryfall.client import ScryfallClient
from api.routes.auth import get_current_user
from db.models import User
from api.schemas.card_schemas import CardResponse, SearchResponse
from api.utils.card_utils import card_model_to_response

router = APIRouter(prefix="/api/cards", tags=["cards"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/search", response_model=SearchResponse)
def search_cards(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Search cards in the database."""
    # Build search query
    query = db.query(Axis1CardModel)
    
    # Search in name (case-insensitive)
    if q:
        search_term = f"%{q}%"
        # Try to search in the name column first (faster)
        query = query.filter(Axis1CardModel.name.ilike(search_term))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    cards = query.offset(offset).limit(page_size).all()
    
    # Convert to response models
    card_responses = [card_model_to_response(card) for card in cards]
    
    return SearchResponse(
        cards=card_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(cards)) < total
    )


@router.get("/random", response_model=CardResponse)
def get_random_card(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a random card from the database."""
    card = db.query(Axis1CardModel).order_by(func.random()).first()
    if not card:
        raise HTTPException(status_code=404, detail="No cards found")
    return card_model_to_response(card)


@router.get("/versions/{card_id}", response_model=List[CardResponse])
def get_card_versions(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all versions (printings) of a card by looking up the card's name."""
    # Get the card to find its name
    card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Use the name field from the model to find all versions
    card_name = card.name
    if not card_name:
        raise HTTPException(status_code=404, detail="Card name not found")
    
    # Find all cards with the same name
    all_versions = db.query(Axis1CardModel).filter(
        Axis1CardModel.name == card_name
    ).all()
    
    return [card_model_to_response(c) for c in all_versions]


@router.get("/{card_id}", response_model=CardResponse)
def get_card(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a card by ID."""
    card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return card_model_to_response(card)


@router.get("", response_model=SearchResponse)
def list_cards(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List cards with pagination."""
    query = db.query(Axis1CardModel)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    cards = query.offset(offset).limit(page_size).all()
    
    # Convert to response models
    card_responses = [card_model_to_response(card) for card in cards]
    
    return SearchResponse(
        cards=card_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(cards)) < total
    )

