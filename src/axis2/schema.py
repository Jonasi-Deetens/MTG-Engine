from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any

# Type aliases for common patterns
EffectList = List['Effect']
CostList = List['Cost']
SubjectFilter = Dict[str, Any]

@dataclass
class Effect:
    """
    Base class for all effects in Axis2.
    
    Effects represent actions or modifications that can be applied to the game state.
    All specific effect types inherit from this base class.
    """
    pass

@dataclass
class Condition:
    kind: str
    zone: Optional[str] = None
    subject: Optional[str] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

# Structured condition classes for semantic representation
@dataclass
class PermanentCondition:
    """Represents a condition about controlling a permanent with specific characteristics."""
    name: Optional[str] = None  # Exact card name (e.g., "Urza's Power-Plant")
    subtypes: Optional[List[str]] = None  # Subtypes (e.g., ["Urza's", "Power-Plant"])
    types: Optional[List[str]] = None  # Types (e.g., ["Land"])
    controller: str = "you"  # "you", "opponent", "any_player"
    
@dataclass
class ControlCondition:
    """Represents a condition about controlling permanents."""
    all_of: Optional[List[PermanentCondition]] = None  # All conditions must be true (AND)
    any_of: Optional[List[PermanentCondition]] = None  # Any condition must be true (OR)
    controller: str = "you"  # "you", "opponent", "any_player"
    
    def __post_init__(self):
        """Ensure at least one of all_of or any_of is set."""
        if not self.all_of and not self.any_of:
            raise ValueError("ControlCondition must have either all_of or any_of")

@dataclass
class ParseContext:
    card_name: str
    primary_type: str
    face_name: str
    face_types: list[str]
    is_spell_text: bool = False
    is_static_ability: bool = False
    is_triggered_ability: bool = False
    
    def with_flag(self, flag_name: str, value: bool) -> 'ParseContext':
        """
        Create a new ParseContext with a flag set to the given value.
        Useful for creating context variants without duplicating base data.
        
        Args:
            flag_name: Name of the flag to set ("is_spell_text", "is_static_ability", "is_triggered_ability")
            value: Value to set the flag to
            
        Returns:
            New ParseContext instance with the flag set
        """
        kwargs = {
            'card_name': self.card_name,
            'primary_type': self.primary_type,
            'face_name': self.face_name,
            'face_types': self.face_types,
            'is_spell_text': self.is_spell_text,
            'is_static_ability': self.is_static_ability,
            'is_triggered_ability': self.is_triggered_ability,
        }
        kwargs[flag_name] = value
        return ParseContext(**kwargs)


@dataclass
class Subject:
    """
    Represents the target or scope of an effect.
    
    Fields:
        scope: How many objects are affected. Valid values:
            - "target": Single target (must be specified)
            - "each": All matching objects
            - "any_number": Player chooses any number
            - "up_to_n": Up to N objects
            - "all": All matching objects (synonym for "each")
            - None: Scope not specified (uses default)
        controller: Who controls the affected objects. Valid values:
            - "you": Objects you control
            - "opponent": Objects opponent controls
            - "any": Any player's objects
            - "opponents": Objects any opponent controls
            - "controller": The controller of the source object
            - None: Controller not specified
        types: List of card types to filter by (e.g., ["creature"], ["creature", "planeswalker"])
        filters: Additional filters as key-value pairs:
            - {"keyword": "flying"}: Has keyword
            - {"power": ">3"}: Power comparison
            - {"toughness": "<=2"}: Toughness comparison
        max_targets: Maximum number of targets (for "up_to_n" scope)
        index: Index for "up to N targets" selection
    """
    scope: str | None = None
    controller: str | None = None
    types: list[str] | None = None
    filters: Dict[str, Any] | None = None
    max_targets: int | None = None
    index: int | None = None

@dataclass
class DynamicValue:
    kind: str  # e.g. "counter_count"
    counter_type: str | None = None
    subject: Subject | None = None

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
class EscapeCost:
    mana_cost: ManaCost
    exile_count: int
    restriction: Optional[str] = None

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
class AttacksEvent:
    subject: str

@dataclass
class LeavesBattlefieldEvent:
    subject: str

@dataclass
class DiesEvent:
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
    cost: Optional['Cost']  # Union of all cost types (ManaCost, TapCost, etc.)
    conditions: List[str] 
    effects: List['Effect']  # List of Effect objects
    kind: str | None = None

@dataclass
class ScryEffect(Effect):
    amount: int

@dataclass
class AddCountersEffect(Effect):
    counter_type: str
    count: str | int  # "times_paid" or a number
    subject: Subject

@dataclass 
class DestroyEffect(Effect): 
    subject: Subject 
    regenerate: bool = False # default: cannot regenerate unless card says so

@dataclass
class SurveilEffect(Effect):
    amount: int

@dataclass
class CantBeBlockedEffect(Effect):
    subject: str              # e.g. "target_creature"
    duration: str      

@dataclass
class ConditionalEffect(Effect):
    condition: str          # e.g. "exiled_this_way", "if_you_do"
    effects: List[Effect]  # list of Effect objects to run if condition is true 

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
    source_zone: str | None = None
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
    counters: Dict[str, int] | None = None
    attach_to: str | None = None

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
class RemoveCounterEffect(Effect):
    counter_type: str
    amount: int = 1  # Default to 1 if not specified
    subject: Subject | None = None  # "it", "this permanent", etc.

@dataclass
class DraftFromSpellbookEffect(Effect):
    source: str

@dataclass
class CreateTokenEffect(Effect):
    amount: Union[int, SymbolicValue]
    token: Dict[str, Any]  # { "power": 1, "toughness": 1, "colors": [...], "types": [...], "abilities": [...] }
    controller: str      # "you", "opponent", "that_player", etc.

@dataclass
class DealDamageEffect(Effect):
    amount: Union[int, SymbolicValue]
    subject: Subject     # Changed from str to Subject for consistency

@dataclass
class DrawCardsEffect(Effect):
    amount: Union[int, SymbolicValue]

@dataclass
class DiscardEffect(Effect):
    """
    Represents a discard effect: "target player discards a card"
    """
    subject: Subject  # Usually Subject(scope="target", types=["player"])
    amount: Union[int, SymbolicValue] = 1  # Number of cards to discard

@dataclass
class AddManaEffect(Effect):
    mana: List[str]      # ["{R}", "{G}", "{1}", "{X}"]
    choice: Optional[str] = None  # "one_color", "any_color"
    # Conditional replacement: if condition is met, use replacement_mana instead
    condition: Optional[str] = None  # Condition text (for backward compatibility / DSL interpreter)
    condition_obj: Optional['ControlCondition'] = None  # Structured condition object (semantic)
    replacement_mana: Optional[List[str]] = None  # Replacement mana if condition is met
    # Conditional replacement: if condition is met, use replacement_mana instead
    condition: Optional[str] = None  # Condition text, e.g., "you control an Urza's Power-Plant and an Urza's Tower"
    replacement_mana: Optional[List[str]] = None  # Replacement mana if condition is met

@dataclass
class SearchEffect(Effect):
    zones: list[str]                 # ["graveyard", "hand", "library"]
    card_names: list[str]            # ["Magnifying Glass", "Thinking Cap"]
    optional: bool                   # "you may"
    put_onto_battlefield: bool       # true
    shuffle_if_library_searched: bool
    card_filter: Dict[str, Any] | None = None  # {"types": ["land"], "subtypes": ["basic"]}, or None
    max_results: int | None = None  # 1, 2, X, or None for unlimited

@dataclass
class ShuffleEffect(Effect):
    subject: Subject   # usually Subject(scope="you")

@dataclass
class RevealEffect(Effect):
    subject: Subject   # usually "searched_cards"

@dataclass
class TransformEffect(Effect):
    subject: Subject
    # optionally, later:
    # mode: Literal["toggle", "to_front", "to_back"] | None = None

@dataclass
class GainLifeEffect(Effect):
    amount: Union[int, SymbolicValue]  # Changed from str for consistency
    subject: str

@dataclass
class PutOntoBattlefieldEffect(Effect):
    """Represents: put a card from a zone onto the battlefield."""
    zone_from: str
    card_filter: Dict[str, Any]
    tapped: bool = False
    attacking: bool = False
    optional: bool = False
    constraint: Optional[Dict[str, Any]] = None

@dataclass
class GrantCastingPermissionEffect(Effect):
    """
    Grants permission to cast spells from a specific zone.
    
    Examples:
    - "you may cast a creature spell from that player's graveyard this turn"
    - "you may cast spells from your graveyard"
    
    Fields:
        from_zone: Zone to cast from ("graveyard", "exile", "library", "hand")
        spell_filter: Filter for which spells can be cast (types, controller, etc.)
        duration: How long the permission lasts ("this_turn", "until_end_of_turn", "permanent")
        mana_modification: Optional mana cost modification
            - "any_color": Spend mana as though it were mana of any color
            - "colorless": Can pay with any color
            - None: No modification
    """
    from_zone: str
    spell_filter: Dict[str, Any]  # e.g., {"types": ["creature"], "controller": "that_player"}
    duration: str = "this_turn"  # "this_turn", "until_end_of_turn", "permanent"
    mana_modification: Optional[str] = None  # "any_color", "colorless", None

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
    """
    Represents an activated ability (cost: effect).
    
    Fields:
        costs: List of costs to activate. Can include:
            - ManaCost: Mana payment
            - TapCost: Tapping requirement
            - SacrificeCost: Sacrifice requirement
            - LoyaltyCost: Planeswalker loyalty change
        effects: List of effects that happen when activated
        conditions: Additional conditions (e.g., "only as a sorcery")
        targeting: Targeting rules if the ability targets
        timing: When the ability can be activated. Valid values:
            - "instant": Any time you have priority
            - "sorcery": Only during your main phase when stack is empty
        is_mana_ability: True if this is a mana ability (doesn't use stack, can't be countered)
            Mana abilities must: produce mana, not target, have no non-mana effects
    """
    costs: List[Cost]
    effects: List[Effect]
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    targeting: Optional[TargetingRules] = None
    timing: str = "instant"
    is_mana_ability: bool = False

@dataclass
class GrantedAbility:
    kind: str                  # e.g. "ward", "flying", "first_strike"
    value: Optional[int] = None  # ward value, or None for abilities without parameters

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
    condition_text: str
    effects: List[Effect]
    event: Optional[Union[ZoneChangeEvent, DealsDamageEvent, EntersBattlefieldEvent, AttacksEvent,
                         LeavesBattlefieldEvent, CastSpellEvent, DiesEvent, str]] = None
    targeting: Optional[TargetingRules] = None
    trigger_filter: Optional[TriggerFilter] = None


@dataclass
class StaticEffect(Effect):
    """
    Represents a static effect that is always active while the object is in relevant zones.
    
    Static effects create continuous effects but are themselves always "on" while
    the source object is in the specified zones.
    
    Fields:
        kind: Type of static effect. Common values:
            - "blocking_restriction": Limits how many creatures can block
            - "haste": Grants haste
            - "cost_modification": Modifies costs
            - "timing_override": Changes timing rules (e.g., "as though it had flash")
        subject: What this effect applies to
        value: Effect-specific value dictionary (varies by kind)
        layer: MTG layer number (1-7) where this effect is applied
        zones: List of zones where this effect is active. Valid zones:
            - "battlefield": While on the battlefield
            - "hand": While in hand
            - "graveyard": While in graveyard
            - "exile": While exiled
            - "stack": While on the stack
        sublayer: Sublayer for layer 7 effects ("7a", "7b", "7c", "7d", "7e")
        protection_from: List of things the subject has protection from
    """
    kind: str
    subject: Subject
    value: Dict[str, Any]
    layer: int  # MTG layers 1-7
    zones: List[str]
    sublayer: Optional[str] = None
    protection_from: Optional[list[str]] = None

@dataclass
class ReplacementEffect(Effect):
    kind: str
    event: str
    subject: Subject
    value: Dict[str, Any]
    zones: List[str]

    # NEW FIELDS FOR DELAYED REPLACEMENT EFFECTS
    next_event_only: bool = False          # "the next time"
    duration: Optional[str] = None         # "until_end_of_turn", "this_turn", etc.
    linked_to: Optional[str] = None        # ID or tag for linked effects
    text: Optional[str] = None

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
class RestrictionData:
    colors: Optional[List[str]] = None
    types: Optional[List[str]] = None
    power_lte: Optional[int] = None
    power_gte: Optional[int] = None
    toughness_lte: Optional[int] = None
    toughness_gte: Optional[int] = None
    keyword: Optional[str] = None

@dataclass
class RuleChangeData:
    kind: str                       # e.g. "targeting_requirement"
    requires_flagbearer: bool = False
    requires_this: bool = False     # for "must choose this creature if able"
    requires_filter: Optional[str] = None  # generalized pattern
    controller: Optional[str] = None       # "opponent", "you", etc.

@dataclass
class ContinuousEffect(Effect):
    """
    Represents a continuous effect that modifies game rules or object characteristics.
    
    Continuous effects are applied in MTG layer order (1-7) with sublayers for layer 7.
    They persist for a duration (e.g., "until end of turn", "as long as...").
    
    Fields:
        kind: Type of continuous effect. Common values:
            - "pt_mod": Power/toughness modification (+X/+Y)
            - "pt_set": Power/toughness setting (becomes X/Y)
            - "grant_ability": Grants an ability (flying, trample, etc.)
            - "color_set": Sets colors
            - "color_add": Adds colors
            - "type_set": Sets types
            - "type_add": Adds types
            - "type_remove": Removes types
            - "grant_protection": Grants protection from X
            - "rule_change": Changes game rules
        text: Original oracle text sentence that created this effect
        layer: MTG layer number (1-7) where this effect is applied. Required.
            - Layer 1: Copy effects
            - Layer 2: Control-changing effects
            - Layer 3: Text-changing effects
            - Layer 4: Type-changing effects
            - Layer 5: Color-changing effects
            - Layer 6: Ability-adding/removing effects
            - Layer 7: Power/toughness effects (with sublayers 7a-7e)
        applies_to: What this effect applies to (Subject or string like "equipped_creature")
        duration: How long the effect lasts (e.g., "until_end_of_turn", "as_long_as_controlled")
        sublayer: Sublayer for layer 7 effects. Valid values: "7a", "7b", "7c", "7d", "7e"
        source_kind: What created this effect ("static_ability", "spell", "ability")
        source_id: Reference to the source ability/effect
        source_object_id: Which object created this effect
        timestamp: When created (for dependency ordering)
        depends_on: List of effect IDs this depends on
        condition: Optional condition for the effect
        pt_value: Power/toughness expression (for pt_mod/pt_set)
        dynamic: Dynamic value calculation
        abilities: List of granted abilities (for grant_ability)
        type_change: Type change data (for type effects)
        color_change: Color change data (for color effects)
        control_change: Control change data
        cost_change: Cost modification
        rule_change: Rule change data
        protection_from: List of things to protect from
        restriction: Restriction data
    """
    kind: str
    text: str
    layer: int  # 1-7 (MTG layers) - REQUIRED, must come before optional fields
    applies_to: Optional[Union[Subject, str]] = None  # "equipped_creature", "creatures_you_control", ...
    duration: Optional[str] = None
    sublayer: Optional[str] = None  # "7a", "7b", "7c", "7d", "7e" for layer 7
    
    # Source tracking (for dependency ordering)
    source_kind: str = "static_ability"  # "static_ability", "spell", "ability"
    source_id: Optional[str] = None  # Reference to source ability/effect
    source_object_id: Optional[str] = None  # Which object created this effect
    timestamp: Optional[int] = None  # When created (for dependency ordering)
    depends_on: Optional[List[str]] = None  # IDs of effects this depends on

    # Optional semantic fields (only one is filled depending on kind)
    condition: Optional[str] = None
    pt_value: Optional[PTExpression] = None
    dynamic: DynamicValue | None = None #
    abilities: Optional[List[GrantedAbility]] = None
    type_change: Optional[TypeChangeData] = None
    color_change: Optional[ColorChangeData] = None
    control_change: Optional[str] = None
    cost_change: Optional[str] = None
    rule_change: Optional[RuleChangeData] = None  # Fixed: removed duplicate, kept RuleChangeData
    protection_from: Optional[List[str]] = None
    restriction: Optional[RestrictionData] = None

@dataclass
class Mode(Effect):
    text: str
    effects: List[Effect]
    targeting: Optional[TargetingRules] = None

@dataclass
class CastingOption:
    kind: str  # "escape", "flashback", "overload", etc.
    mana_cost: Optional[ManaCost]
    additional_costs: List[Dict[str, Any]] = field(default_factory=list)  # e.g., [{"time_counters": 3}, {"power": 2, "toughness": 3}]

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

    casting_options: List[CastingOption] = field(default_factory=list)
    spell_effects: List[Effect] = field(default_factory=list)
    spell_targeting: Optional[TargetingRules] = None
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
