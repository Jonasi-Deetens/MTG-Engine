# src/api/routes/collections.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from db.connection import SessionLocal
from db.models import User, UserFavorite, Collection, CollectionItem, Axis1CardModel
from api.routes.auth import get_current_user
from api.schemas.card_schemas import CardResponse
from api.utils.card_utils import card_model_to_response

router = APIRouter(prefix="/api/collections", tags=["collections"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Request/Response models
class FavoriteResponse(BaseModel):
    card_id: str
    card: CardResponse
    created_at: str

    class Config:
        from_attributes = True


class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    card_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CollectionDetailResponse(CollectionResponse):
    cards: List[CardResponse]


class CollectionItemAdd(BaseModel):
    card_id: str


# Favorites endpoints
@router.get("/favorites", response_model=List[FavoriteResponse])
def get_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's favorite cards."""
    offset = (page - 1) * page_size
    favorites = db.query(UserFavorite).filter(
        UserFavorite.user_id == user.id
    ).offset(offset).limit(page_size).all()
    
    result = []
    for fav in favorites:
        card = db.query(Axis1CardModel).filter(
            Axis1CardModel.card_id == fav.card_id
        ).first()
        if card:
            result.append(FavoriteResponse(
                card_id=fav.card_id,
                card=card_model_to_response(card),
                created_at=fav.created_at.isoformat()
            ))
    
    return result


@router.post("/favorites", response_model=dict)
def add_favorite(
    item: CollectionItemAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add a card to favorites."""
    # Check if card exists
    card = db.query(Axis1CardModel).filter(
        Axis1CardModel.card_id == item.card_id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Check if already favorited
    existing = db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == user.id,
            UserFavorite.card_id == item.card_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Card already in favorites")
    
    favorite = UserFavorite(
        user_id=user.id,
        card_id=item.card_id
    )
    db.add(favorite)
    db.commit()
    
    return {"message": "Card added to favorites", "card_id": item.card_id}


@router.delete("/favorites/{card_id}", response_model=dict)
def remove_favorite(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Remove a card from favorites."""
    favorite = db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == user.id,
            UserFavorite.card_id == card_id
        )
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Card removed from favorites"}


@router.get("/favorites/{card_id}/check", response_model=dict)
def check_favorite(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Check if a card is favorited."""
    favorite = db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == user.id,
            UserFavorite.card_id == card_id
        )
    ).first()
    
    return {"is_favorite": favorite is not None}


# Collections endpoints
@router.get("", response_model=List[CollectionResponse])
def get_collections(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's collections."""
    collections = db.query(Collection).filter(
        Collection.user_id == user.id
    ).all()
    
    result = []
    for coll in collections:
        card_count = db.query(CollectionItem).filter(
            CollectionItem.collection_id == coll.id
        ).count()
        result.append(CollectionResponse(
            id=coll.id,
            name=coll.name,
            description=coll.description,
            card_count=card_count,
            created_at=coll.created_at.isoformat(),
            updated_at=coll.updated_at.isoformat()
        ))
    
    return result


@router.post("", response_model=CollectionResponse)
def create_collection(
    collection: CollectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new collection."""
    new_collection = Collection(
        user_id=user.id,
        name=collection.name,
        description=collection.description
    )
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    
    return CollectionResponse(
        id=new_collection.id,
        name=new_collection.name,
        description=new_collection.description,
        card_count=0,
        created_at=new_collection.created_at.isoformat(),
        updated_at=new_collection.updated_at.isoformat()
    )


@router.get("/{collection_id}", response_model=CollectionDetailResponse)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a collection with its cards."""
    collection = db.query(Collection).filter(
        and_(
            Collection.id == collection_id,
            Collection.user_id == user.id
        )
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    items = db.query(CollectionItem).filter(
        CollectionItem.collection_id == collection_id
    ).all()
    
    cards = []
    for item in items:
        card = db.query(Axis1CardModel).filter(
            Axis1CardModel.card_id == item.card_id
        ).first()
        if card:
            cards.append(card_model_to_response(card))
    
    return CollectionDetailResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        card_count=len(cards),
        created_at=collection.created_at.isoformat(),
        updated_at=collection.updated_at.isoformat(),
        cards=cards
    )


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int,
    collection: CollectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update a collection."""
    coll = db.query(Collection).filter(
        and_(
            Collection.id == collection_id,
            Collection.user_id == user.id
        )
    ).first()
    
    if not coll:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if collection.name is not None:
        coll.name = collection.name
    if collection.description is not None:
        coll.description = collection.description
    coll.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(coll)
    
    card_count = db.query(CollectionItem).filter(
        CollectionItem.collection_id == collection_id
    ).count()
    
    return CollectionResponse(
        id=coll.id,
        name=coll.name,
        description=coll.description,
        card_count=card_count,
        created_at=coll.created_at.isoformat(),
        updated_at=coll.updated_at.isoformat()
    )


@router.delete("/{collection_id}", response_model=dict)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a collection."""
    collection = db.query(Collection).filter(
        and_(
            Collection.id == collection_id,
            Collection.user_id == user.id
        )
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection deleted"}


@router.post("/{collection_id}/cards", response_model=dict)
def add_card_to_collection(
    collection_id: int,
    item: CollectionItemAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Add a card to a collection."""
    # Verify collection belongs to user
    collection = db.query(Collection).filter(
        and_(
            Collection.id == collection_id,
            Collection.user_id == user.id
        )
    ).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Check if card exists
    card = db.query(Axis1CardModel).filter(
        Axis1CardModel.card_id == item.card_id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Check if already in collection
    existing = db.query(CollectionItem).filter(
        and_(
            CollectionItem.collection_id == collection_id,
            CollectionItem.card_id == item.card_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Card already in collection")
    
    collection_item = CollectionItem(
        collection_id=collection_id,
        card_id=item.card_id
    )
    db.add(collection_item)
    db.commit()
    
    return {"message": "Card added to collection", "card_id": item.card_id}


@router.delete("/{collection_id}/cards/{card_id}", response_model=dict)
def remove_card_from_collection(
    collection_id: int,
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Remove a card from a collection."""
    # Verify collection belongs to user
    collection = db.query(Collection).filter(
        and_(
            Collection.id == collection_id,
            Collection.user_id == user.id
        )
    ).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    item = db.query(CollectionItem).filter(
        and_(
            CollectionItem.collection_id == collection_id,
            CollectionItem.card_id == card_id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Card not found in collection")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Card removed from collection"}

