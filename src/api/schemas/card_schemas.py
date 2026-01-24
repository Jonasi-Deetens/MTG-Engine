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
    color_identity: List[str] = []
    card_types: List[str] = []
    supertypes: List[str] = []
    subtypes: List[str] = []
    keywords: List[str] = []
    produced_mana: List[str] = []
    image_uris: Optional[dict]
    set_code: Optional[str]
    set_name: Optional[str] = None
    set_type: Optional[str] = None
    layout: Optional[str] = None
    released_at: Optional[str] = None
    collector_number: Optional[str]
    rarity: Optional[str] = None
    legalities: Optional[dict] = None
    prices: Optional[dict] = None
    artist: Optional[str] = None
    flavor_text: Optional[str] = None
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    cards: List[CardResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

