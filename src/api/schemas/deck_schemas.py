# src/api/schemas/deck_schemas.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from api.schemas.card_schemas import CardResponse


class DeckCardResponse(BaseModel):
    card_id: str
    card: CardResponse
    quantity: int
    list_id: Optional[int] = None

    class Config:
        from_attributes = True


class DeckCommanderResponse(BaseModel):
    card_id: str
    card: CardResponse
    position: int

    class Config:
        from_attributes = True


class DeckCreate(BaseModel):
    name: str
    description: Optional[str] = None
    format: str  # Commander, Standard, Modern, etc.
    is_public: bool = False


class DeckUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    format: Optional[str] = None
    is_public: Optional[bool] = None


class DeckResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    format: str
    is_public: bool
    card_count: int
    commander_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class DeckDetailResponse(DeckResponse):
    cards: List[DeckCardResponse]
    commanders: List[DeckCommanderResponse]


class DeckCardAdd(BaseModel):
    card_id: str
    quantity: int = 1
    list_id: Optional[int] = None


class DeckCardUpdate(BaseModel):
    quantity: int


class DeckCommanderAdd(BaseModel):
    card_id: str
    position: int = 0


class ValidationError(BaseModel):
    type: str  # "error" or "warning"
    message: str
    field: Optional[str] = None


class DeckValidationResponse(BaseModel):
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    card_count: int
    commander_count: int
    format: str


class DeckImportRequest(BaseModel):
    format: str  # "text" or "json"
    data: str  # The deck list data


class DeckExportResponse(BaseModel):
    format: str
    data: str
    deck_name: str
    format_type: str


class DeckCustomListCreate(BaseModel):
    name: str
    position: Optional[int] = 0


class DeckCustomListUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None


class DeckCustomListResponse(BaseModel):
    id: int
    deck_id: int
    name: str
    position: int
    created_at: datetime

    class Config:
        from_attributes = True


class DeckCardListUpdate(BaseModel):
    list_id: Optional[int] = None

