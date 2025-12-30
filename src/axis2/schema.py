from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any

@dataclass
class SymbolicValue:
    kind: str            # "star", "variable", "formula"
    expression: str      # "*", "X", "*+1", etc.

@dataclass
class ManaCost:
    symbols: List[str]   # ["{R}", "{1}", "{U}"]

@dataclass
class TapCost:
    amount: int
    restrictions: list[str]   # e.g. ["artifact", "untapped", "you_control"]

@dataclass
class SacrificeCost:
    subject: str         # "this", "creature", etc.

@dataclass
class LoyaltyCost:
    amount: int          # +1, -3, 0

Cost = Union[ManaCost, TapCost, SacrificeCost, LoyaltyCost]

@dataclass 
class SpecialAction: 
    name: str 
    cost: Optional[object] # usually ManaCost 
    conditions: List[str] 
    effects: List[object]

@dataclass
class DayboundEffect:
    pass

@dataclass
class CantBeBlockedEffect:
    subject: str              # e.g. "target_creature"
    duration: str             # e.g. "until_end_of_turn"

@dataclass
class NightboundEffect:
    pass

@dataclass
class EquipEffect:
    """
    Semantic effect representing the Equip keyword ability.
    Axis2 does not interpret this; Axis3 implements the rules.
    """
    pass

@dataclass
class CounterSpellEffect:
    """Represents: counter that spell / counter target spell."""
    target: str  # usually "that_spell" or "target_spell"

@dataclass
class PutCounterEffect:
    counter_type: str
    amount: int

@dataclass
class CreateTokenEffect:
    amount: Union[int, SymbolicValue]
    token: dict          # { "power": 1, "toughness": 1, "colors": [...], "types": [...], "abilities": [...] }
    controller: str      # "you", "opponent", "that_player", etc.

@dataclass
class DealDamageEffect:
    amount: Union[int, SymbolicValue]
    subject: str         # "any_target", "target_creature", etc.

@dataclass
class DrawCardsEffect:
    amount: Union[int, SymbolicValue]

@dataclass
class AddManaEffect:
    mana: List[str]      # ["{R}", "{G}", "{1}", "{X}"]
    choice: Optional[str] = None  # "one_color", "any_color"

Effect = Union[
    DealDamageEffect,
    DrawCardsEffect,
    AddManaEffect,
    CreateTokenEffect,
]

@dataclass
class SearchEffect:
    zones: list[str]                 # ["graveyard", "hand", "library"]
    card_names: list[str]            # ["Magnifying Glass", "Thinking Cap"]
    optional: bool                   # "you may"
    put_onto_battlefield: bool       # true
    shuffle_if_library_searched: bool

@dataclass
class GainLifeEffect:
    amount: str
    subject: str

@dataclass
class PutOntoBattlefieldEffect:
    """Represents: put a card from a zone onto the battlefield."""
    zone_from: str
    card_filter: dict
    tapped: bool = False
    attacking: bool = False
    constraint: Optional[dict] = None
    optional: bool = False

@dataclass
class TargetingRestriction:
    type: str
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    logic: Optional[str] = None  # "AND", "OR"

@dataclass
class TargetingRules:
    required: bool = False
    min: int = 0
    max: int = 0
    legal_targets: List[str] = field(default_factory=list)
    restrictions: List[TargetingRestriction] = field(default_factory=list)

@dataclass
class ActivatedAbility:
    costs: List[Cost]
    effects: List[Effect]
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    targeting: Optional[TargetingRules] = None
    timing: str = "instant"   # "instant", "sorcery", etc.

@dataclass
class TriggerFilter:
    """
    Structured, machine-readable trigger conditions.
    Axis3 uses this instead of parsing English.
    """
    spell_must_have_types: list[str] = field(default_factory=list)
    spell_must_not_have_types: list[str] = field(default_factory=list)
    controller_scope: str | None = None   # "any_player", "you", "opponent", etc.

@dataclass
class TriggeredAbility:
    event: str
    condition_text: str
    effects: list
    targeting: Optional[TargetingRules] = None
    trigger_filter: Optional[TriggerFilter] = None


@dataclass
class StaticEffect:
    kind: str
    subject: str
    value: Dict[str, Any]
    layer: str
    zones: List[str]

@dataclass
class ReplacementEffect:
    kind: str                 # "as_enters", "dies_to_exile", "prevent_damage", "draw_instead", ...
    text: str                 # original text
    applies_to: Optional[str] = None
    amount: Optional[str] = None          # "all", "1", "X", etc.
    new_action: Optional[str] = None      # "exile", "draw_extra", "prevent", "redirect"
    condition: Optional[str] = None       # "if it's your turn", "if it's a creature", etc.

@dataclass
class PTExpression:
    power: str
    toughness: str

@dataclass
class ColorChangeData:
    set_colors: Optional[list[str]] = None
    add_colors: Optional[list[str]] = None

@dataclass
class TypeChangeData:
    set_types: Optional[list[str]] = None
    add_types: Optional[list[str]] = None
    remove_types: Optional[list[str]] = None

@dataclass
class ContinuousEffect:
    kind: str                 # "pt_mod", "grant_ability", "color_set", ...
    applies_to: str           # "equipped_creature", "creatures_you_control", ...
    text: str                 # original sentence

    # Optional semantic fields (only one is filled depending on kind)
    condition: Optional[str] = None
    pt_value: Optional[PTExpression] = None
    abilities: Optional[list[str]] = None
    type_change: Optional[TypeChangeData] = None
    color_change: Optional[ColorChangeData] = None
    control_change: Optional[str] = None
    cost_change: Optional[str] = None
    rule_change: Optional[str] = None

@dataclass
class Mode:
    text: str
    effects: List[Effect]
    targeting: Optional[TargetingRules] = None

@dataclass
class Axis2Face:
    name: str
    mana_cost: Optional[ManaCost]
    mana_value: float
    colors: List[str]
    types: List[str]
    supertypes: List[str]
    subtypes: List[str]

    power: Optional[Union[int, SymbolicValue]]
    toughness: Optional[Union[int, SymbolicValue]]
    loyalty: Optional[int]
    defense: Optional[int]

    special_actions: List[SpecialAction] = field(default_factory=list)
    activated_abilities: List[ActivatedAbility] = field(default_factory=list)
    triggered_abilities: List[TriggeredAbility] = field(default_factory=list)
    static_effects: List[StaticEffect] = field(default_factory=list)
    replacement_effects: List[ReplacementEffect] = field(default_factory=list)
    continuous_effects: List[ContinuousEffect] = field(default_factory=list)
    modes: List[Mode] = field(default_factory=list)

@dataclass
class Axis2Characteristics:
    mana_cost: Optional[ManaCost]
    mana_value: Optional[float]

    colors: List[str]
    color_identity: List[str]
    color_indicator: List[str]

    types: List[str]
    supertypes: List[str]
    subtypes: List[str]

    power: Optional[Union[int, SymbolicValue]]
    toughness: Optional[Union[int, SymbolicValue]]
    loyalty: Optional[int]
    defense: Optional[int]

@dataclass
class Axis2Card:
    card_id: str
    oracle_id: Optional[str]
    set: str
    collector_number: str

    faces: List[Axis2Face]
    characteristics: Axis2Characteristics

    keywords: List[str] = field(default_factory=list)
