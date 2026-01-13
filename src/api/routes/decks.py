# src/api/routes/decks.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict
from datetime import datetime

from db.connection import SessionLocal
from db.models import User, Deck, DeckCard, DeckCommander, DeckCustomList, Axis1CardModel
from api.routes.auth import get_current_user
from api.schemas.deck_schemas import (
    DeckCreate, DeckUpdate, DeckResponse, DeckDetailResponse,
    DeckCardAdd, DeckCardUpdate, DeckCardResponse,
    DeckCommanderAdd, DeckCommanderResponse,
    DeckValidationResponse, DeckImportRequest, DeckExportResponse,
    DeckCustomListCreate, DeckCustomListUpdate, DeckCustomListResponse,
    DeckCardListUpdate
)
from api.schemas.card_schemas import CardResponse
from api.utils.card_utils import card_model_to_response
from api.utils.deck_validator import validate_deck

router = APIRouter(prefix="/api/decks", tags=["decks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[DeckResponse])
def get_decks(
    format_filter: Optional[str] = Query(None, alias="format"),
    is_public: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's decks with optional filters."""
    query = db.query(Deck).filter(Deck.user_id == user.id)
    
    if format_filter:
        query = query.filter(Deck.format == format_filter)
    if is_public is not None:
        query = query.filter(Deck.is_public == is_public)
    
    decks = query.order_by(Deck.updated_at.desc()).all()
    
    result = []
    for deck in decks:
        card_count = db.query(func.sum(DeckCard.quantity)).filter(
            DeckCard.deck_id == deck.id
        ).scalar() or 0
        
        commander_count = db.query(DeckCommander).filter(
            DeckCommander.deck_id == deck.id
        ).count()
        
        result.append(DeckResponse(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            format=deck.format,
            is_public=deck.is_public,
            card_count=int(card_count),
            commander_count=commander_count,
            created_at=deck.created_at.isoformat(),
            updated_at=deck.updated_at.isoformat()
        ))
    
    return result


@router.post("", response_model=DeckResponse)
def create_deck(
    deck: DeckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new deck."""
    new_deck = Deck(
        user_id=user.id,
        name=deck.name,
        description=deck.description,
        format=deck.format,
        is_public=deck.is_public
    )
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    
    return DeckResponse(
        id=new_deck.id,
        name=new_deck.name,
        description=new_deck.description,
        format=new_deck.format,
        is_public=new_deck.is_public,
        card_count=0,
        commander_count=0,
        created_at=new_deck.created_at.isoformat(),
        updated_at=new_deck.updated_at.isoformat()
    )


@router.get("/{deck_id}", response_model=DeckDetailResponse)
def get_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get deck details with cards and commanders."""
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Get cards
    deck_cards = db.query(DeckCard).filter(DeckCard.deck_id == deck_id).all()
    cards = []
    for dc in deck_cards:
        card = db.query(Axis1CardModel).filter(
            Axis1CardModel.card_id == dc.card_id
        ).first()
        if card:
            cards.append(DeckCardResponse(
                card_id=dc.card_id,
                card=card_model_to_response(card),
                quantity=dc.quantity,
                list_id=getattr(dc, 'list_id', None)
            ))
    
    # Get commanders
    deck_commanders = db.query(DeckCommander).filter(
        DeckCommander.deck_id == deck_id
    ).order_by(DeckCommander.position).all()
    commanders = []
    for dc in deck_commanders:
        card = db.query(Axis1CardModel).filter(
            Axis1CardModel.card_id == dc.card_id
        ).first()
        if card:
            commanders.append(DeckCommanderResponse(
                card_id=dc.card_id,
                card=card_model_to_response(card),
                position=dc.position
            ))
    
    card_count = sum(c.quantity for c in cards)
    
    return DeckDetailResponse(
        id=deck.id,
        name=deck.name,
        description=deck.description,
        format=deck.format,
        is_public=deck.is_public,
        card_count=card_count,
        commander_count=len(commanders),
        created_at=deck.created_at.isoformat(),
        updated_at=deck.updated_at.isoformat(),
        cards=cards,
        commanders=commanders
    )


@router.put("/{deck_id}", response_model=DeckResponse)
def update_deck(
    deck_id: int,
    deck: DeckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update deck metadata."""
    deck_obj = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    
    if not deck_obj:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    if deck.name is not None:
        deck_obj.name = deck.name
    if deck.description is not None:
        deck_obj.description = deck.description
    if deck.format is not None:
        deck_obj.format = deck.format
    if deck.is_public is not None:
        deck_obj.is_public = deck.is_public
    deck_obj.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(deck_obj)
    
    card_count = db.query(func.sum(DeckCard.quantity)).filter(
        DeckCard.deck_id == deck_id
    ).scalar() or 0
    
    commander_count = db.query(DeckCommander).filter(
        DeckCommander.deck_id == deck_id
    ).count()
    
    return DeckResponse(
        id=deck_obj.id,
        name=deck_obj.name,
        description=deck_obj.description,
        format=deck_obj.format,
        is_public=deck_obj.is_public,
        card_count=int(card_count),
        commander_count=commander_count,
        created_at=deck_obj.created_at.isoformat(),
        updated_at=deck_obj.updated_at.isoformat()
    )


@router.delete("/{deck_id}", response_model=dict)
def delete_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a deck."""
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    db.delete(deck)
    db.commit()
    
    return {"message": "Deck deleted"}


@router.post("/{deck_id}/cards", response_model=DeckCardResponse)
def add_card_to_deck(
    deck_id: int,
    card: DeckCardAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add a card to a deck."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Check if card exists
    card_model = db.query(Axis1CardModel).filter(
        Axis1CardModel.card_id == card.card_id
    ).first()
    if not card_model:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Check if card already in deck
    existing = db.query(DeckCard).filter(
        and_(
            DeckCard.deck_id == deck_id,
            DeckCard.card_id == card.card_id
        )
    ).first()
    
    if existing:
        existing.quantity += card.quantity
        if hasattr(card, 'list_id') and card.list_id is not None:
            if hasattr(existing, 'list_id'):
                existing.list_id = card.list_id
        db.commit()
        # Only refresh if list_id column exists to avoid errors
        try:
            db.refresh(existing)
        except Exception:
            pass
        quantity = existing.quantity
        list_id = getattr(existing, 'list_id', None)
    else:
        deck_card = DeckCard(
            deck_id=deck_id,
            card_id=card.card_id,
            quantity=card.quantity
        )
        if hasattr(card, 'list_id') and hasattr(deck_card, 'list_id'):
            deck_card.list_id = card.list_id
        db.add(deck_card)
        db.commit()
        # Only refresh if list_id column exists to avoid errors
        try:
            db.refresh(deck_card)
        except Exception:
            pass
        quantity = deck_card.quantity
        list_id = getattr(deck_card, 'list_id', None)
    
    return DeckCardResponse(
        card_id=card.card_id,
        card=card_model_to_response(card_model),
        quantity=quantity,
        list_id=list_id
    )


@router.put("/{deck_id}/cards/{card_id}", response_model=DeckCardResponse)
def update_card_quantity(
    deck_id: int,
    card_id: str,
    card: DeckCardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update card quantity in deck."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    deck_card = db.query(DeckCard).filter(
        and_(
            DeckCard.deck_id == deck_id,
            DeckCard.card_id == card_id
        )
    ).first()
    
    if not deck_card:
        raise HTTPException(status_code=404, detail="Card not found in deck")
    
    if card.quantity <= 0:
        db.delete(deck_card)
        db.commit()
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    deck_card.quantity = card.quantity
    db.commit()
    # Only refresh if list_id column exists to avoid errors
    try:
        db.refresh(deck_card)
    except Exception:
        # Column doesn't exist yet, skip refresh - we already have the quantity
        pass
    
    card_model = db.query(Axis1CardModel).filter(
        Axis1CardModel.card_id == card_id
    ).first()
    
    return DeckCardResponse(
        card_id=card_id,
        card=card_model_to_response(card_model),
        quantity=deck_card.quantity,
        list_id=getattr(deck_card, 'list_id', None)
    )


@router.delete("/{deck_id}/cards/{card_id}", response_model=dict)
def remove_card_from_deck(
    deck_id: int,
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Remove a card from a deck."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    deck_card = db.query(DeckCard).filter(
        and_(
            DeckCard.deck_id == deck_id,
            DeckCard.card_id == card_id
        )
    ).first()
    
    if not deck_card:
        raise HTTPException(status_code=404, detail="Card not found in deck")
    
    db.delete(deck_card)
    db.commit()
    
    return {"message": "Card removed from deck"}


@router.post("/{deck_id}/commanders", response_model=DeckCommanderResponse)
def add_commander(
    deck_id: int,
    commander: DeckCommanderAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add a commander to a deck."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Check if card exists
    card_model = db.query(Axis1CardModel).filter(
        Axis1CardModel.card_id == commander.card_id
    ).first()
    if not card_model:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Check if already a commander
    existing = db.query(DeckCommander).filter(
        and_(
            DeckCommander.deck_id == deck_id,
            DeckCommander.card_id == commander.card_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Card already set as commander")
    
    # Check commander count (max 2)
    commander_count = db.query(DeckCommander).filter(
        DeckCommander.deck_id == deck_id
    ).count()
    if commander_count >= 2:
        raise HTTPException(status_code=400, detail="Maximum 2 commanders allowed")
    
    deck_commander = DeckCommander(
        deck_id=deck_id,
        card_id=commander.card_id,
        position=commander.position
    )
    db.add(deck_commander)
    db.commit()
    db.refresh(deck_commander)
    
    return DeckCommanderResponse(
        card_id=commander.card_id,
        card=card_model_to_response(card_model),
        position=deck_commander.position
    )


@router.delete("/{deck_id}/commanders/{card_id}", response_model=dict)
def remove_commander(
    deck_id: int,
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Remove a commander from a deck."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    commander = db.query(DeckCommander).filter(
        and_(
            DeckCommander.deck_id == deck_id,
            DeckCommander.card_id == card_id
        )
    ).first()
    
    if not commander:
        raise HTTPException(status_code=404, detail="Commander not found")
    
    db.delete(commander)
    db.commit()
    
    return {"message": "Commander removed"}


@router.get("/{deck_id}/validate", response_model=DeckValidationResponse)
def validate_deck_endpoint(
    deck_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Validate a deck against format rules."""
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Get cards
    deck_cards = db.query(DeckCard).filter(DeckCard.deck_id == deck_id).all()
    card_quantities: Dict[str, int] = {}
    card_names: Dict[str, str] = {}
    card_rarities: Dict[str, str] = {}
    card_count = 0
    
    for dc in deck_cards:
        card = db.query(Axis1CardModel).filter(
            Axis1CardModel.card_id == dc.card_id
        ).first()
        if card:
            card_quantities[dc.card_id] = dc.quantity
            card_data = card.axis1_json or {}
            faces = card_data.get("faces", [])
            first_face = faces[0] if faces else {}
            card_names[dc.card_id] = first_face.get("name") or card_data.get("name", "")
            # Extract rarity if available
            card_rarities[dc.card_id] = card_data.get("rarity", "")
            card_count += dc.quantity
    
    # Get commanders
    commanders = db.query(DeckCommander).filter(
        DeckCommander.deck_id == deck_id
    ).all()
    commander_count = len(commanders)
    
    # Validate
    validation = validate_deck(
        format_type=deck.format,
        card_count=card_count,
        commander_count=commander_count,
        card_quantities=card_quantities,
        card_names=card_names,
        card_rarities=card_rarities
    )
    
    return validation


@router.post("/import", response_model=DeckDetailResponse)
def import_deck(
    import_data: DeckImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Import a deck from text or JSON format."""
    # This is a simplified import - full implementation would parse various formats
    # For now, we'll create a basic structure
    # TODO: Implement full text/JSON parsing
    
    raise HTTPException(status_code=501, detail="Import functionality not yet implemented")


@router.get("/{deck_id}/export", response_model=DeckExportResponse)
def export_deck(
    deck_id: int,
    format: str = Query("text", description="Export format: text or json"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Export a deck as text or JSON."""
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Get cards
    deck_cards = db.query(DeckCard).filter(DeckCard.deck_id == deck_id).all()
    
    if format.lower() == "text":
        lines = [f"{deck.name}\n"]
        if deck.description:
            lines.append(f"{deck.description}\n")
        lines.append(f"\nFormat: {deck.format}\n\n")
        
        for dc in deck_cards:
            card = db.query(Axis1CardModel).filter(
                Axis1CardModel.card_id == dc.card_id
            ).first()
            if card:
                card_data = card.axis1_json or {}
                faces = card_data.get("faces", [])
                first_face = faces[0] if faces else {}
                card_name = first_face.get("name") or card_data.get("name", "")
                lines.append(f"{dc.quantity} {card_name}\n")
        
        return DeckExportResponse(
            format="text",
            data="".join(lines),
            deck_name=deck.name,
            format_type=deck.format
        )
    else:  # JSON
        import json
        cards_data = []
        for dc in deck_cards:
            card = db.query(Axis1CardModel).filter(
                Axis1CardModel.card_id == dc.card_id
            ).first()
            if card:
                cards_data.append({
                    "card_id": dc.card_id,
                    "quantity": dc.quantity
                })
        
        export_data = {
            "name": deck.name,
            "description": deck.description,
            "format": deck.format,
            "cards": cards_data
        }
        
        return DeckExportResponse(
            format="json",
            data=json.dumps(export_data, indent=2),
            deck_name=deck.name,
            format_type=deck.format
        )


# Custom List Endpoints

@router.post("/{deck_id}/lists", response_model=DeckCustomListResponse)
def create_custom_list(
    deck_id: int,
    custom_list: DeckCustomListCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a custom list for organizing deck cards."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    new_list = DeckCustomList(
        deck_id=deck_id,
        name=custom_list.name,
        position=custom_list.position or 0
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    
    return DeckCustomListResponse(
        id=new_list.id,
        deck_id=new_list.deck_id,
        name=new_list.name,
        position=new_list.position,
        created_at=new_list.created_at
    )


@router.get("/{deck_id}/lists", response_model=List[DeckCustomListResponse])
def get_custom_lists(
    deck_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all custom lists for a deck."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    custom_lists = db.query(DeckCustomList).filter(
        DeckCustomList.deck_id == deck_id
    ).order_by(DeckCustomList.position).all()
    
    return [
        DeckCustomListResponse(
            id=cl.id,
            deck_id=cl.deck_id,
            name=cl.name,
            position=cl.position,
            created_at=cl.created_at
        )
        for cl in custom_lists
    ]


@router.put("/{deck_id}/lists/{list_id}", response_model=DeckCustomListResponse)
def update_custom_list(
    deck_id: int,
    list_id: int,
    custom_list: DeckCustomListUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update a custom list's name or position."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    custom_list_obj = db.query(DeckCustomList).filter(
        and_(
            DeckCustomList.id == list_id,
            DeckCustomList.deck_id == deck_id
        )
    ).first()
    
    if not custom_list_obj:
        raise HTTPException(status_code=404, detail="Custom list not found")
    
    if custom_list.name is not None:
        custom_list_obj.name = custom_list.name
    if custom_list.position is not None:
        custom_list_obj.position = custom_list.position
    
    db.commit()
    db.refresh(custom_list_obj)
    
    return DeckCustomListResponse(
        id=custom_list_obj.id,
        deck_id=custom_list_obj.deck_id,
        name=custom_list_obj.name,
        position=custom_list_obj.position,
        created_at=custom_list_obj.created_at
    )


@router.delete("/{deck_id}/lists/{list_id}", response_model=dict)
def delete_custom_list(
    deck_id: int,
    list_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a custom list. Cards in this list will have their list_id set to null."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    custom_list = db.query(DeckCustomList).filter(
        and_(
            DeckCustomList.id == list_id,
            DeckCustomList.deck_id == deck_id
        )
    ).first()
    
    if not custom_list:
        raise HTTPException(status_code=404, detail="Custom list not found")
    
    # Set all cards in this list to have list_id = null
    # Only if the column exists in the database
    try:
        db.query(DeckCard).filter(
            and_(
                DeckCard.deck_id == deck_id,
                DeckCard.list_id == list_id
            )
        ).update({DeckCard.list_id: None})
    except Exception:
        # Column doesn't exist yet, skip (migration not run)
        pass
    
    # Delete the list
    db.delete(custom_list)
    db.commit()
    
    return {"message": "Custom list deleted"}


@router.put("/{deck_id}/cards/{card_id}/list", response_model=DeckCardResponse)
def move_card_to_list(
    deck_id: int,
    card_id: str,
    update: DeckCardListUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Move a card to a custom list (or remove from list if list_id is null)."""
    # Verify deck belongs to user
    deck = db.query(Deck).filter(
        and_(
            Deck.id == deck_id,
            Deck.user_id == user.id
        )
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Verify list exists if list_id is provided
    if update.list_id is not None:
        custom_list = db.query(DeckCustomList).filter(
            and_(
                DeckCustomList.id == update.list_id,
                DeckCustomList.deck_id == deck_id
            )
        ).first()
        if not custom_list:
            raise HTTPException(status_code=404, detail="Custom list not found")
    
    deck_card = db.query(DeckCard).filter(
        and_(
            DeckCard.deck_id == deck_id,
            DeckCard.card_id == card_id
        )
    ).first()
    
    if not deck_card:
        raise HTTPException(status_code=404, detail="Card not found in deck")
    
    if hasattr(deck_card, 'list_id'):
        deck_card.list_id = update.list_id
    db.commit()
    db.refresh(deck_card)
    
    card_model = db.query(Axis1CardModel).filter(
        Axis1CardModel.card_id == card_id
    ).first()
    
    return DeckCardResponse(
        card_id=card_id,
        card=card_model_to_response(card_model),
        quantity=deck_card.quantity,
        list_id=getattr(deck_card, 'list_id', None)
    )

