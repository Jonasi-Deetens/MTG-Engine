# src/api/routes/cards.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from pydantic import BaseModel

from db.connection import SessionLocal
from db.models import Axis1CardModel
from db.repository import Axis1Repository
from scryfall.client import ScryfallClient
from api.routes.auth import get_current_user
from db.models import User

router = APIRouter(prefix="/api/cards", tags=["cards"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Response models
class CardResponse(BaseModel):
    card_id: str
    oracle_id: Optional[str]
    name: str
    mana_cost: Optional[str]
    mana_value: Optional[int]
    type_line: Optional[str]
    oracle_text: Optional[str]
    power: Optional[str]
    toughness: Optional[str]
    colors: List[str]
    image_uris: Optional[dict]
    set_code: Optional[str]
    collector_number: Optional[str]
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    cards: List[CardResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


def _card_model_to_response(card_model: Axis1CardModel) -> CardResponse:
    """Convert Axis1CardModel to CardResponse."""
    card_data = card_model.axis1_json or {}
    faces = card_data.get("faces", [])
    first_face = faces[0] if faces else {}
    
    return CardResponse(
        card_id=card_model.card_id,
        oracle_id=card_data.get("oracle_id"),
        name=first_face.get("name") or card_data.get("name", ""),
        mana_cost=first_face.get("mana_cost") or card_data.get("mana_cost"),
        mana_value=first_face.get("mana_value") or card_data.get("mana_value"),
        type_line=first_face.get("type_line") or card_data.get("type_line"),
        oracle_text=first_face.get("oracle_text") or card_data.get("oracle_text"),
        power=first_face.get("power") or card_data.get("power"),
        toughness=first_face.get("toughness") or card_data.get("toughness"),
        colors=first_face.get("colors", []) or card_data.get("colors", []),
        image_uris=first_face.get("image_uris") or card_data.get("image_uris"),
        set_code=card_model.set_code,
        collector_number=card_model.collector_number
    )


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
    card_responses = [_card_model_to_response(card) for card in cards]
    
    return SearchResponse(
        cards=card_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(cards)) < total
    )


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
    
    return _card_model_to_response(card)


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
    card_responses = [_card_model_to_response(card) for card in cards]
    
    return SearchResponse(
        cards=card_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(cards)) < total
    )

