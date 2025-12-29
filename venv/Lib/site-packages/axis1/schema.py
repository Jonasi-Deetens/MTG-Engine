from typing import List, Optional, Dict, Any
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
    raw: str                           # Full original line
    cost: str                          # Everything before colon
    cost_parts: List[Dict[str, Any]] = Field(default_factory=list)
    effect: str                        # Everything after colon
    cost_metadata: Dict[str, Any] = Field(default_factory=dict)
    activation_conditions: List[Dict[str, Any]] = Field(default_factory=list)

class Axis1Face(BaseModel):
    face_id: str = "front"
    name: str
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None
    colors: List[str] = []
    color_indicator: List[str] = []
    card_types: List[str] = []
    supertypes: List[str] = []
    subtypes: List[str] = []
    power: Optional[int] = None
    toughness: Optional[int] = None
    loyalty: Optional[int] = None
    defense: Optional[int] = None
    hand_modifier: Optional[int] = None
    life_modifier: Optional[int] = None

    oracle_text: Optional[str] = None
    printed_text: Optional[str] = None
    flavor_text: Optional[str] = None

    keywords: List[str] = []
    ability_words: List[str] = []
    static_abilities: List[str] = []
    activated_abilities: List[Axis1ActivatedAbility] = []
    triggered_abilities: List[Axis1TriggeredAbility] = []
    reminder_text: List[str] = []

    has_characteristic_defining_abilities: bool = False
    characteristic_defining_abilities: List[str] = []

    intrinsic_counters: List[IntrinsicCounter] = []
    attachment: Optional[AttachmentRules] = None
    face_layout_rules: FaceLayoutRules = FaceLayoutRules()

class Axis1Characteristics(BaseModel):
    mana_cost: Optional[str] = None
    mana_value: Optional[float] = None
    colors: List[str] = []
    color_identity: List[str] = []
    color_indicator: List[str] = []
    card_types: List[str] = []
    supertypes: List[str] = []
    subtypes: List[str] = []
    power: Optional[int] = None
    toughness: Optional[int] = None
    loyalty: Optional[int] = None
    defense: Optional[int] = None


class Axis1Metadata(BaseModel):
    rarity: Optional[str] = None
    artist: Optional[str] = None
    illustration_id: Optional[str] = None
    frame: Optional[str] = None
    border_color: Optional[str] = None
    watermark: Optional[str] = None
    legalities: Dict[str, str] = {}
    image_uris: Dict[str, str] = {}


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

    intrinsic_rules: List[str] = []
    intrinsic_limits: List[IntrinsicLimit] = []
    intrinsic_counters: List[IntrinsicCounter] = []

    zones_allowed: List[str] = [
      "Library", "Hand", "Stack", "Battlefield", "Graveyard", "Exile"
    ]

    characteristic_sources: Dict[str, str] = {}
    rules_tags: List[str] = []

    metadata: Axis1Metadata = Axis1Metadata()
