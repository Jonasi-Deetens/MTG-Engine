from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, root_validator


class Initiation(str, Enum):
    STATIC = "static"
    TRIGGERED = "triggered"
    ACTIVATED = "activated"


class Resolution(str, Enum):
    STACK = "stack"
    IMMEDIATE = "immediate"


class Persistence(str, Enum):
    INSTANT = "instant"
    CONTINUOUS = "continuous"


class EffectTag(str, Enum):
    MANA = "mana"
    LAND = "land"
    REPLACEMENT = "replacement"
    PREVENTION = "prevention"
    CDA = "cda"
    KEYWORD = "keyword"
    LOYALTY = "loyalty"


class SourceKind(str, Enum):
    SPELL = "spell"
    PERMANENT = "permanent"


class ConditionSpec(BaseModel):
    type: str

    class Config:
        extra = "allow"


class TriggerSpec(BaseModel):
    event: str
    scope: Optional[str] = "self"
    cardType: Optional[str] = None
    entersWhere: Optional[str] = None
    entersFrom: Optional[str] = None

    class Config:
        extra = "allow"


class CostItem(BaseModel):
    type: str
    amount: Optional[Union[int, str]] = None
    manaType: Optional[str] = None

    class Config:
        extra = "allow"


class CostSpec(BaseModel):
    items: List[CostItem] = Field(default_factory=list)
    timing: Optional[str] = None
    limit: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class DurationWhileInZone(BaseModel):
    type: Literal["while_in_zone"]
    zone: str


class DurationUntilEndOfTurn(BaseModel):
    type: Literal["until_end_of_turn"]


class DurationUntilEndOfCombat(BaseModel):
    type: Literal["until_end_of_combat"]


class DurationUntilYourNextTurn(BaseModel):
    type: Literal["until_your_next_turn"]


class DurationUntilCondition(BaseModel):
    type: Literal["until_condition"]
    condition: ConditionSpec


Duration = Union[
    DurationWhileInZone,
    DurationUntilEndOfTurn,
    DurationUntilEndOfCombat,
    DurationUntilYourNextTurn,
    DurationUntilCondition,
]


class OneShotAction(BaseModel):
    type: str

    class Config:
        extra = "allow"


class ModifierSpec(BaseModel):
    type: str

    class Config:
        extra = "allow"


class OneShotEffect(BaseModel):
    kind: Literal["one_shot"]
    action: OneShotAction


class ContinuousEffect(BaseModel):
    kind: Literal["continuous"]
    layer: int
    modifier: ModifierSpec
    appliesTo: Optional[Dict[str, Any]] = None
    duration: Duration

    class Config:
        extra = "allow"


class ReplacementEffect(BaseModel):
    kind: Literal["replacement"]
    replaces: Dict[str, Any]
    with_: Dict[str, Any] = Field(alias="with")

    class Config:
        populate_by_name = True
        extra = "allow"


class PreventionEffect(BaseModel):
    kind: Literal["prevention"]
    prevents: Dict[str, Any]
    amount: Optional[Union[int, str, Dict[str, Any]]] = None

    class Config:
        extra = "allow"


EffectBody = Union[OneShotEffect, ContinuousEffect, ReplacementEffect, PreventionEffect]


class UnifiedEffect(BaseModel):
    id: str
    initiation: Initiation
    resolution: Resolution = Resolution.STACK
    persistence: Persistence = Persistence.INSTANT
    tags: List[EffectTag] = Field(default_factory=list)
    trigger: Optional[TriggerSpec] = None
    cost: Optional[CostSpec] = None
    conditions: List[ConditionSpec] = Field(default_factory=list)
    effect: EffectBody

    class Config:
        extra = "allow"

    @root_validator
    def _validate_initiation_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        initiation = values.get("initiation")
        if initiation == Initiation.TRIGGERED and values.get("trigger") is None:
            raise ValueError("trigger is required when initiation is 'triggered'")
        if initiation == Initiation.ACTIVATED and values.get("cost") is None:
            raise ValueError("cost is required when initiation is 'activated'")
        return values

    @root_validator
    def _validate_resolution_tags(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        tags = values.get("tags") or []
        resolution = values.get("resolution")
        if EffectTag.MANA in tags and resolution != Resolution.IMMEDIATE:
            raise ValueError("mana-tagged effects must resolve immediately")
        return values

    @root_validator
    def _validate_persistence_effect_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        effect = values.get("effect")
        persistence = values.get("persistence")
        if isinstance(effect, ContinuousEffect) and persistence != Persistence.CONTINUOUS:
            raise ValueError("continuous effect bodies require persistence='continuous'")
        return values


class EffectStep(BaseModel):
    id: str
    effect: UnifiedEffect
    next: Optional[List[str]] = None
    nextByMode: Optional[Dict[str, str]] = None


class EffectGraph(BaseModel):
    id: str
    sourceKind: SourceKind = SourceKind.PERMANENT
    steps: List[EffectStep]
    modal: Optional[Dict[str, Any]] = None


class CardEffectGraphResponse(BaseModel):
    id: int
    card_id: str
    effect_graph: EffectGraph
    created_at: str
    updated_at: str


class EffectValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
