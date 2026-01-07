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

class Axis1TriggeredAbility(BaseModel):
    raw: str
    condition: str
    effect: str
    event_hint: str

class AttachmentRules(BaseModel):
    can_attach_to: List[str] = []
    default_targeting: bool = False

class Axis1ActivatedAbility(BaseModel):
    raw: str
    cost: str
    cost_parts: List[Dict[str, Any]] = Field(default_factory=list)
    effect: str
    cost_metadata: Dict[str, Any] = Field(default_factory=dict)

    # FIX: allow strings OR dicts
    activation_conditions: List[Dict[str, Any]] = Field(default_factory=list)


class Axis1Face(BaseModel):
    face_id: str = "front"
    name: str

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

    keywords: List[str] = Field(default_factory=list)
    ability_words: List[str] = Field(default_factory=list)
    static_abilities: List[str] = Field(default_factory=list)

    # ⭐ Allow activation conditions as strings OR dicts
    activated_abilities: List[Axis1ActivatedAbility] = Field(default_factory=list)
    triggered_abilities: List[Axis1TriggeredAbility] = Field(default_factory=list)

    reminder_text: List[str] = Field(default_factory=list)

    has_characteristic_defining_abilities: bool = False
    characteristic_defining_abilities: List[str] = Field(default_factory=list)

    intrinsic_counters: List[IntrinsicCounter] = Field(default_factory=list)
    attachment: Optional[AttachmentRules] = None
    face_layout_rules: FaceLayoutRules = Field(default_factory=FaceLayoutRules)


class Axis1Characteristics(BaseModel):
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None

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

    legalities: Dict[str, str] = Field(default_factory=dict)
    image_uris: Dict[str, str] = Field(default_factory=dict)
    prices: Dict[str, Optional[str]] = Field(default_factory=dict)  # usd, usd_foil, eur, tix, etc.


class Axis1Card(BaseModel):
    card_id: str = Field(..., description="Unique card UUID (Scryfall id)")
    oracle_id: Optional[str] = None
    scryfall_id: Optional[str] = None
    set: Optional[str] = None
    collector_number: Optional[str] = None
    lang: Optional[str] = None

    layout: str
    object_kind: str = "card"

    names: List[str]
    printed_name: Optional[str] = None
    default_face: str = "front"
    can_transform: bool = False
    transform_condition: Optional[str] = None

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
