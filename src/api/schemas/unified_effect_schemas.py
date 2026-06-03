from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


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


class ConditionType(str, Enum):
    CONTROL_COUNT = "control_count"
    LIFE_TOTAL = "life_total"
    MANA_AVAILABLE = "mana_available"
    BATTLEFIELD_COUNT = "battlefield_count"
    GRAVEYARD_COUNT = "graveyard_count"
    HAND_COUNT = "hand_count"
    POWER_COMPARISON = "power_comparison"
    TOUGHNESS_COMPARISON = "toughness_comparison"
    IS_TYPE = "is_type"
    IS_TAPPED = "is_tapped"
    IS_ATTACKING = "is_attacking"
    IS_BLOCKING = "is_blocking"
    HAS_KEYWORD = "has_keyword"
    HAS_COUNTER = "has_counter"
    IS_CAST = "is_cast"
    WAS_CAST = "was_cast"
    MANA_VALUE_COMPARISON = "mana_value_comparison"
    KICKED = "kicked"
    KICKER_COUNT = "kicker_count"
    CREATURES_IN_GRAVEYARD = "creatures_in_graveyard"
    PREVIOUS_EFFECT_RESULT_COUNT = "previous_effect_result_count"
    PREVIOUS_EFFECT_HAS_RESULT = "previous_effect_has_result"


class ConditionSpec(BaseModel):
    type: ConditionType

    class Config:
        extra = "allow"


class TriggerSpec(BaseModel):
    event: str
    scope: Optional[str] = "self"
    cardType: Optional[Union[str, List[str]]] = None
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


class OptionalCostSpec(BaseModel):
    kind: str
    tag: Optional[str] = None
    repeatable: Optional[bool] = None
    costs: List[CostItem] = Field(default_factory=list)

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

    @model_validator(mode="after")
    def _validate_initiation_fields(self) -> "UnifiedEffect":
        if self.initiation == Initiation.TRIGGERED and self.trigger is None:
            raise ValueError("trigger is required when initiation is 'triggered'")
        if self.initiation == Initiation.ACTIVATED and self.cost is None:
            raise ValueError("cost is required when initiation is 'activated'")
        return self

    @model_validator(mode="after")
    def _validate_resolution_tags(self) -> "UnifiedEffect":
        if EffectTag.MANA in (self.tags or []) and self.resolution != Resolution.IMMEDIATE:
            raise ValueError("mana-tagged effects must resolve immediately")
        return self

    @model_validator(mode="after")
    def _validate_persistence_effect_kind(self) -> "UnifiedEffect":
        if isinstance(self.effect, ContinuousEffect) and self.persistence != Persistence.CONTINUOUS:
            raise ValueError("continuous effect bodies require persistence='continuous'")
        return self


class EffectStep(BaseModel):
    id: str
    effect: UnifiedEffect
    next: Optional[List[str]] = None
    nextByMode: Optional[Dict[str, str]] = None


class EffectGraph(BaseModel):
    id: str
    sourceKind: SourceKind = SourceKind.PERMANENT
    steps: List[EffectStep]
    additionalCosts: Optional[List[CostItem]] = None
    optionalCosts: Optional[List[OptionalCostSpec]] = None
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
