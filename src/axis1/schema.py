# axis1/schema.py

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class IntrinsicCounter(BaseModel):
    type: str
    amount: int


class IntrinsicLimit(BaseModel):
    action: str
    limit: str


class FaceLayoutSagaChapter(BaseModel):
    chapter: int
    rules: str


class FaceLayoutAdventure(BaseModel):
    is_adventure: bool = False
    adventure_name: Optional[str] = None
    adventure_cost: Optional[str] = None
    adventure_type_line: Optional[str] = None
    adventure_text: Optional[str] = None


class FaceLayoutPrototype(BaseModel):
    is_prototype: bool = False
    prototype_cost: Optional[str] = None
    prototype_power: Optional[str] = None
    prototype_toughness: Optional[str] = None
    prototype_colors: List[str] = []


class FaceLayoutLeveler(BaseModel):
    is_leveler: bool = False
    levels: List[Dict[str, Any]] = []


class FaceLayoutRules(BaseModel):
    saga_chapters: List[FaceLayoutSagaChapter] = []
    battle_defense: Optional[int] = None
    adventure: FaceLayoutAdventure = FaceLayoutAdventure()
    prototype: FaceLayoutPrototype = FaceLayoutPrototype()
    leveler: FaceLayoutLeveler = FaceLayoutLeveler()

class AttachmentRules(BaseModel):
    can_attach_to: List[str] = []
    default_targeting: bool = False


class Axis1Face(BaseModel):
    face_id: str = "front"
    name: str
    type_line: Optional[str] = None

    # Lands have no mana cost → allow None
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None

    # Scryfall uses null for colorless cards → default_factory
    colors: List[str] = Field(default_factory=list)
    color_indicator: List[str] = Field(default_factory=list)

    card_types: List[str] = Field(default_factory=list)
    supertypes: List[str] = Field(default_factory=list)
    subtypes: List[str] = Field(default_factory=list)

    # ⭐ Allow symbolic values: "*", "X", "*+1", etc.
    power: Optional[Union[str, int]] = None
    toughness: Optional[Union[str, int]] = None
    loyalty: Optional[Union[str, int]] = None
    defense: Optional[Union[str, int]] = None

    hand_modifier: Optional[int] = None
    life_modifier: Optional[int] = None

    oracle_text: Optional[str] = None
    printed_text: Optional[str] = None
    flavor_text: Optional[str] = None
    image_uris: Dict[str, str] = Field(default_factory=dict)

    keywords: List[str] = Field(default_factory=list)
    ability_words: List[str] = Field(default_factory=list)
    static_abilities: List[str] = Field(default_factory=list)
    produced_mana: List[str] = Field(default_factory=list)

    reminder_text: List[str] = Field(default_factory=list)

    has_characteristic_defining_abilities: bool = False
    characteristic_defining_abilities: List[str] = Field(default_factory=list)

    intrinsic_counters: List[IntrinsicCounter] = Field(default_factory=list)
    attachment: Optional[AttachmentRules] = None
    face_layout_rules: FaceLayoutRules = Field(default_factory=FaceLayoutRules)


class Axis1Characteristics(BaseModel):
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None
    type_line: Optional[str] = None

    colors: List[str] = Field(default_factory=list)
    color_identity: List[str] = Field(default_factory=list)
    color_indicator: List[str] = Field(default_factory=list)

    card_types: List[str] = Field(default_factory=list)
    supertypes: List[str] = Field(default_factory=list)
    subtypes: List[str] = Field(default_factory=list)

    # ⭐ Allow symbolic values
    power: Optional[Union[str, int]] = None
    toughness: Optional[Union[str, int]] = None
    loyalty: Optional[Union[str, int]] = None
    defense: Optional[Union[str, int]] = None

class Axis1Metadata(BaseModel):
    rarity: Optional[str] = None
    artist: Optional[str] = None
    illustration_id: Optional[str] = None
    frame: Optional[str] = None
    border_color: Optional[str] = None
    watermark: Optional[str] = None
    set_name: Optional[str] = None
    set_type: Optional[str] = None
    released_at: Optional[str] = None
    reserved: Optional[bool] = None
    digital: Optional[bool] = None
    promo: Optional[bool] = None
    reprint: Optional[bool] = None
    variation: Optional[bool] = None
    full_art: Optional[bool] = None
    oversized: Optional[bool] = None
    foil: Optional[bool] = None
    nonfoil: Optional[bool] = None
    finishes: List[str] = Field(default_factory=list)
    games: List[str] = Field(default_factory=list)
    security_stamp: Optional[str] = None

    legalities: Dict[str, str] = Field(default_factory=dict)
    image_uris: Dict[str, str] = Field(default_factory=dict)
    prices: Dict[str, Optional[str]] = Field(default_factory=dict)  # usd, usd_foil, eur, tix, etc.

class Axis1SearchIndex(BaseModel):
    name: str
    names: List[str] = Field(default_factory=list)
    type_line: Optional[str] = None
    colors: List[str] = Field(default_factory=list)
    color_identity: List[str] = Field(default_factory=list)
    card_types: List[str] = Field(default_factory=list)
    supertypes: List[str] = Field(default_factory=list)
    subtypes: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    produced_mana: List[str] = Field(default_factory=list)
    mana_value: Optional[float] = None
    power: Optional[Union[str, int]] = None
    toughness: Optional[Union[str, int]] = None
    loyalty: Optional[Union[str, int]] = None
    defense: Optional[Union[str, int]] = None
    rarity: Optional[str] = None
    set_code: Optional[str] = None
    set_name: Optional[str] = None
    set_type: Optional[str] = None
    layout: Optional[str] = None
    released_at: Optional[str] = None
    oracle_text: Optional[str] = None

class Axis1Card(BaseModel):
    card_id: str = Field(..., description="Unique card UUID (Scryfall id)")
    oracle_id: Optional[str] = None
    scryfall_id: Optional[str] = None
    set: Optional[str] = None
    set_name: Optional[str] = None
    set_type: Optional[str] = None
    collector_number: Optional[str] = None
    lang: Optional[str] = None

    layout: str
    object_kind: str = "card"

    name: str
    names: List[str]
    printed_name: Optional[str] = None
    default_face: str = "front"
    can_transform: bool = False
    transform_condition: Optional[str] = None
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None
    colors: List[str] = Field(default_factory=list)
    color_identity: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    produced_mana: List[str] = Field(default_factory=list)
    power: Optional[Union[str, int]] = None
    toughness: Optional[Union[str, int]] = None
    loyalty: Optional[Union[str, int]] = None
    defense: Optional[Union[str, int]] = None
    released_at: Optional[str] = None

    faces: List[Axis1Face]

    characteristics: Axis1Characteristics

    intrinsic_rules: List[str] = Field(default_factory=list)
    intrinsic_limits: List[IntrinsicLimit] = Field(default_factory=list)
    intrinsic_counters: List[IntrinsicCounter] = Field(default_factory=list)

    zones_allowed: List[str] = Field(
        default_factory=lambda: [
            "Library", "Hand", "Stack", "Battlefield", "Graveyard", "Exile"
        ]
    )

    characteristic_sources: Dict[str, str] = Field(default_factory=dict)
    rules_tags: List[str] = Field(default_factory=list)

    metadata: Axis1Metadata = Field(default_factory=Axis1Metadata)
    search_index: Axis1SearchIndex
