# src/api/schemas/card_schemas.py

from pydantic import BaseModel
from typing import List, Optional


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

