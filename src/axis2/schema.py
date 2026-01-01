from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any

@dataclass
class Effect:
    pass

@dataclass
class ParseContext:
    card_name: str
    primary_type: str
    face_name: str
    face_types: list[str]

@dataclass
class Subject:
    scope: str | None = None          # "target", "each", "any_number", "up_to_n", "all"
    controller: str | None = None     # "you", "opponent", "any", "opponents", "controller"
    types: list[str] | None = None    # ["creature"], ["creature", "planeswalker"], etc.
    filters: dict | None = None       # {"keyword": "flying"}, {"power": ">3"}, etc.
    max_targets: int | None = None    # for "up to N targets"

@dataclass
class SpellFilter:
    must_have_types: list[str] = field(default_factory=list)
    must_not_have_types: list[str] = field(default_factory=list)
    controller_scope: str | None = None   # "you", "opponent", "any"

@dataclass
class CardTypeCountCondition:
    zone: str                     # "graveyard", "library", etc.
    min_types: int | None = None  # e.g. 4
    max_types: int | None = None  # rarely used

@dataclass
class SymbolicValue:
    kind: str            # "star", "variable", "formula"
    expression: str      # "*", "X", "*+1", etc.

@dataclass
class ManaCost:
    symbols: List[str]   # ["{R}", "{1}", "{U}"]

@dataclass
class TapCost:
    amount: int = 1
    subject: Subject = field(default_factory=lambda: Subject(scope="self"))
    restrictions: list[str] = field(default_factory=list)


@dataclass
class DiscardCost:
    amount: int

@dataclass
class SacrificeCost:
    subject: Subject

@dataclass
class LoyaltyCost:
    amount: int          # +1, -3, 0

Cost = Union[ManaCost, TapCost, SacrificeCost, LoyaltyCost]

@dataclass
class DealsDamageEvent:
    subject: str          # who dealt the damage
    target: str           # who/what was damaged
    damage_type: str      # "combat", "noncombat", or "any"

@dataclass
class EntersBattlefieldEvent:
    subject: str

@dataclass
class LeavesBattlefieldEvent:
    subject: str

@dataclass
class ZoneChangeEvent:
    subject: str
    from_zone: str
    to_zone: str

@dataclass
class CastSpellEvent:
    subject: str
    spell_filter: "SpellFilter"

@dataclass 
class SpecialAction: 
    name: str 
    cost: Optional[object] # usually ManaCost 
    conditions: List[str] 
    effects: List[object]
    kind: str | None = None

@dataclass
class ScryEffect(Effect):
    amount: int

@dataclass
class AddCountersEffect:
    counter_type: str
    count: str | int  # "times_paid" or a number
    subject: Subject

@dataclass
class SurveilEffect(Effect):
    amount: int

@dataclass
class CantBeBlockedEffect(Effect):
    subject: str              # e.g. "target_creature"
    duration: str       

@dataclass
class DayboundEffect(Effect):
    pass
      # e.g. "until_end_of_turn"
@dataclass
class NightboundEffect(Effect):
    pass

@dataclass
class LookAndPickEffect(Effect):
    # How many cards to look at
    look_at: int
    # Reveal up to N cards (optional)
    reveal_up_to: int | None = None
    # Types of cards allowed to be revealed (e.g. ["creature"])
    reveal_types: list[str] | None = None
    # Where revealed cards go (e.g. "hand", "battlefield", "graveyard")
    put_revealed_into: str | None = None
    # Where the rest go (e.g. "bottom", "graveyard", "exile")
    put_rest_into: str | None = None
    # Ordering of the rest ("random", "ordered", None)
    rest_order: str | None = None
    # Whether the reveal is optional ("you may reveal…")
    optional: bool = False

@dataclass
class ChangeZoneEffect(Effect):
    subject: Subject
    from_zone: str | None = None
    to_zone: str | None = None
    owner: str | None = None
    position: str | None = None   # Only used for library
    face_down: bool = False
    tapped: bool = False
    counters: dict[str, int] | None = None

@dataclass
class EquipEffect(Effect):
    """
    Semantic effect representing the Equip keyword ability.
    Axis2 does not interpret this; Axis3 implements the rules.
    """
    pass

@dataclass
class CounterSpellEffect(Effect):
    """Represents: counter that spell / counter target spell."""
    target: str  # usually "that_spell" or "target_spell"

@dataclass
class ReturnCardFromGraveyardEffect(Effect):
    subtype: str
    controller: str = "you"
    destination_zone: str = "hand"

@dataclass
class GainLifeEqualToPowerEffect(Effect):
    source: str = "that_card"
    stat: str = "power"         # which stat to read


@dataclass
class PTBoostEffect(Effect):
    power: int
    toughness: int
    duration: str = "until_end_of_turn"

@dataclass
class PutCounterEffect(Effect):
    counter_type: str
    amount: int

@dataclass
class DraftFromSpellbookEffect(Effect):
    source: str

@dataclass
class CreateTokenEffect(Effect):
    amount: Union[int, SymbolicValue]
    token: dict          # { "power": 1, "toughness": 1, "colors": [...], "types": [...], "abilities": [...] }
    controller: str      # "you", "opponent", "that_player", etc.

@dataclass
class DealDamageEffect(Effect):
    amount: Union[int, SymbolicValue]
    subject: str         # "any_target", "target_creature", etc.

@dataclass
class DrawCardsEffect(Effect):
    amount: Union[int, SymbolicValue]

@dataclass
class AddManaEffect(Effect):
    mana: List[str]      # ["{R}", "{G}", "{1}", "{X}"]
    choice: Optional[str] = None  # "one_color", "any_color"

@dataclass
class SearchEffect(Effect):
    zones: list[str]                 # ["graveyard", "hand", "library"]
    card_names: list[str]            # ["Magnifying Glass", "Thinking Cap"]
    optional: bool                   # "you may"
    put_onto_battlefield: bool       # true
    shuffle_if_library_searched: bool

@dataclass
class TransformEffect(Effect):
    subject: Subject
    # optionally, later:
    # mode: Literal["toggle", "to_front", "to_back"] | None = None

@dataclass
class GainLifeEffect(Effect):
    amount: str
    subject: str

@dataclass
class PutOntoBattlefieldEffect(Effect):
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
class StaticEffect(Effect):
    kind: str
    subject: Subject
    value: Dict[str, Any]
    layer: str
    zones: List[str]
    protection_from: Optional[list[str]] = None

@dataclass
class ReplacementEffect(Effect):
    kind: str                     # semantic category: "zone_change_replacement", "prevent_damage", etc.
    event: str                    # the event being replaced: "move_to_graveyard", "would_die", "damage", "draw", etc.
    subject: Subject              # who the replacement applies to
    value: Dict[str, Any]         # structured payload: {"instead": [...]} or {"amount": N} etc.
    zones: List[str]              # where the effect applies ("battlefield", "anywhere", etc.)
    text: Optional[str] = None    # original oracle text (optional but useful)

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
class ContinuousEffect(Effect):
    kind: str                 # "pt_mod", "grant_ability", "color_set", ...
    applies_to: str           # "equipped_creature", "creatures_you_control", ...
    text: str                 # original sentence
    duration: Optional[str] = None

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
class Mode(Effect):
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
