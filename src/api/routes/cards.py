# src/api/routes/cards.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, cast, String, text
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List

from db.connection import SessionLocal
from db.models import Axis1CardModel
from db.repository import Axis1Repository
from scryfall.client import ScryfallClient
from api.routes.auth import get_current_user, get_optional_user
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
    user: Optional[User] = Depends(get_optional_user)
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
    user: Optional[User] = Depends(get_optional_user)
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
    user: Optional[User] = Depends(get_optional_user)
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
    colors: Optional[str] = Query(None, description="Comma-separated color filter (e.g., 'W,U' for white or blue)"),
    type: Optional[str] = Query(None, description="Type filter (searches in type_line)"),
    set_code: Optional[str] = Query(None, description="Set code filter"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    """List cards with pagination and optional filters."""
    query = db.query(Axis1CardModel)
    
    # Filter by set_code (already indexed column)
    if set_code:
        query = query.filter(Axis1CardModel.set_code.ilike(f"%{set_code}%"))
    
    # Filter by colors (stored in JSON)
    if colors:
        color_list = [c.strip().upper() for c in colors.split(',') if c.strip()]
        if color_list:
            # Check if 'C' (colorless) is in the filter
            has_colorless = 'C' in color_list
            color_list_without_c = [c for c in color_list if c != 'C']
            
            # Build color filter conditions
            color_conditions = []
            
            # For cards with colors: check if any of the card's colors match the filter
            if color_list_without_c:
                for color in color_list_without_c:
                    # Use JSONB @> operator to check if array contains the color
                    # Check in faces[0].colors or top-level colors
                    # Note: color is validated (W, U, B, R, G) so safe to use in f-string
                    color_json = f'["{color}"]'
                    color_condition = or_(
                        text(f"axis1_json->'faces'->0->'colors' @> '{color_json}'::jsonb"),
                        text(f"axis1_json->'colors' @> '{color_json}'::jsonb")
                    )
                    color_conditions.append(color_condition)
            
            # For colorless cards: check if colors array is empty or null
            if has_colorless:
                colorless_condition = or_(
                    text("axis1_json->'faces'->0->'colors' IS NULL"),
                    text("axis1_json->'faces'->0->'colors' = '[]'::jsonb"),
                    text("axis1_json->'colors' IS NULL"),
                    text("axis1_json->'colors' = '[]'::jsonb"),
                    text("NOT (axis1_json ? 'faces')"),
                    text("NOT (axis1_json ? 'colors')")
                )
                color_conditions.append(colorless_condition)
            
            if color_conditions:
                query = query.filter(or_(*color_conditions))
    
    # Filter by type (searches in type_line within JSON)
    if type:
        type_lower = type.lower()
        # Search in faces[0].type_line or top-level type_line
        # Use text() for safer JSON path access that handles missing keys
        type_condition = or_(
            text(f"LOWER(CAST(axis1_json->'faces'->0->>'type_line' AS TEXT)) LIKE '%{type_lower}%'"),
            text(f"LOWER(CAST(axis1_json->>'type_line' AS TEXT)) LIKE '%{type_lower}%'")
        )
        query = query.filter(type_condition)
    
    # Get total count (before pagination)
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

