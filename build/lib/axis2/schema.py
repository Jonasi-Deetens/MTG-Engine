from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union

# ------------------------------------------------------------
# BASIC RULE COMPONENTS
# ------------------------------------------------------------

@dataclass
class ReplacementEffect:
    """
    Represents replacement and prevention effects:
      - "If X would die, do Y instead"
      - "Prevent all damage to Z"
      - "If you would draw a card, draw two instead"
      - "Enter the battlefield tapped"
    """
    event: str
    replace_with: Callable[..., None]   # or an Effect object
    condition: Optional[Condition] = None


@dataclass
class StaticEffect:
    """
    Represents static continuous effects, including type-changing effects.
    Applies in the specified zones and participates in layer processing.
    """
    kind: str                     # e.g. "type_changer", "buff", "restriction"
    subject: str                  # "this", "creatures_you_control", etc.
    value: Dict[str, Any]         # effect-specific payload
    layering: str                 # e.g. "layer_4", "layer_7b"
    zones: List[str] = None       # ["battlefield"], ["all"], ["hand","graveyard"], etc.

@dataclass
class TimingRules:
    speed: Optional[str] = None               # "instant", "sorcery", "special"
    phases: List[str] = field(default_factory=list)
    requires_priority: bool = True
    stack_must_be_empty: bool = False


@dataclass
class CostRules:
    mana: Optional[str] = None
    additional: List[str] = field(default_factory=list)
    alternative: List[str] = field(default_factory=list)
    reductions: List[str] = field(default_factory=list)
    increases: List[str] = field(default_factory=list)

@dataclass
class ContinuousEffect:
    effect_type: str
    selector: Selector
    params: dict


@dataclass
class TargetingRestriction:
    type: str
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    logic: Optional[str] = None               # "AND", "OR"
    optional: bool = False


@dataclass
class TargetingRules:
    required: bool = False
    min: int = 0
    max: int = 0
    legal_targets: List[str] = field(default_factory=list)
    restrictions: List[TargetingRestriction] = field(default_factory=list)
    replacement_effects: List[str] = field(default_factory=list)

@dataclass
class Mode:
    text: str
    targeting: TargetingRules

@dataclass
class PermissionRules:
    permissions: List[str] = field(default_factory=list)


@dataclass
class RestrictionRules:
    restrictions: List[str] = field(default_factory=list)


@dataclass
class StateRestrictions:
    state_restrictions: List[str] = field(default_factory=list)


@dataclass
class TurnPermissions:
    controller_only: bool = False
    opponent_only: bool = False


@dataclass
class VisibilityConstraints:
    revealed: bool = False
    randomized: bool = False


# ------------------------------------------------------------
# ACTIONS
# ------------------------------------------------------------

@dataclass
class CastSpellAction:
    allowed: bool = False
    timing: TimingRules = field(default_factory=TimingRules)
    zones: List[str] = field(default_factory=list)
    costs: CostRules = field(default_factory=CostRules)
    restrictions: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    targeting_rules: TargetingRules = field(default_factory=TargetingRules)
    state_restrictions: List[str] = field(default_factory=list)
    turn_permissions: TurnPermissions = field(default_factory=TurnPermissions)
    visibility_constraints: VisibilityConstraints = field(default_factory=VisibilityConstraints)

@dataclass
class PlayLandAction:
    allowed: bool = False
    phases: List[str] = field(default_factory=list)
    requires_priority: bool = False
    limit_per_turn: int = 1
    dynamic_limit_conditions: List[Dict[str, Any]] = field(default_factory=list)
    zones: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    state_restrictions: List[str] = field(default_factory=list)
    turn_permissions: TurnPermissions = field(default_factory=TurnPermissions)


@dataclass
class ActivateAbilityAction:
    allowed: bool = False
    effect_text: str = ""
    ability_id: str = ""
    source: str = "this"
    targeting_rules: TargetingRules = field(default_factory=TargetingRules)
    timing: TimingRules = field(default_factory=TimingRules)
    costs: CostRules = field(default_factory=CostRules)
    restrictions: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    state_restrictions: List[str] = field(default_factory=list)
    turn_permissions: TurnPermissions = field(default_factory=TurnPermissions)
    dynamic_limit_conditions: List[Dict[str, Any]] = field(default_factory=list)
    conditional_usage: List[Dict[str, Any]] = field(default_factory=list)
    visibility_constraints: VisibilityConstraints = field(default_factory=VisibilityConstraints)


@dataclass
class SpecialAction:
    # New, what builder/tests use:
    kind: str = ""                         # e.g. "morph", "foretell"
    cost: Optional[str] = None             # morph/foretell/prototype cost text
    effect: Optional[str] = None           # description of what the action does

    # Existing structural fields (still available if needed):
    zones: List[str] = field(default_factory=list)
    costs: CostRules = field(default_factory=CostRules)
    timing: TimingRules = field(default_factory=TimingRules)
    state_restrictions: List[str] = field(default_factory=list)
    turn_permissions: TurnPermissions = field(default_factory=TurnPermissions)
    conditional_usage: List[Dict[str, Any]] = field(default_factory=list)

    # Optional: backwards-compat alias if anything still references `type`
    @property
    def type(self) -> str:
        return self.kind

    @type.setter
    def type(self, value: str) -> None:
        self.kind = value


# ------------------------------------------------------------
# TRIGGERS
# ------------------------------------------------------------

@dataclass
class Trigger:
    effect_text: str
    event: str
    condition: Optional[str] = None
    mandatory: bool = True


# ------------------------------------------------------------
# GLOBAL RULES
# ------------------------------------------------------------

@dataclass
class ZonePermissions:
    permissions: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class GlobalRestriction:
    applies_to: str
    restriction: str


@dataclass
class Condition:
    type: str
    object: Optional[str] = None
    count: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[Any] = None

@dataclass
class ActionReplacement:
    # What the builder (and likely tests) expect:
    type: str = ""              # kind of replacement ("dies_exile_instead", etc.)
    subject: str = ""           # who/what it applies to ("this", "you", etc.)
    event: str = ""             # original event/action being replaced

    # Older naming / structural fields, kept for compatibility:
    original: str = ""          # can mirror `event` if needed
    replacement: str = ""       # description/key of the replacement
    layer: int = 0
    order: int = 0


@dataclass
class ActionPrevention:
    original: str
    prevention_reason: str
    layer: int
    order: int


@dataclass
class ActionModifier:
    original: str
    modification: str
    layer: int
    order: int


@dataclass
class MandatoryAction:
    action: str
    condition: str


@dataclass
class LimitRule:
    action: str
    limit_type: str
    dynamic: bool = False
    tracking_per_player: bool = False
    amount_per_cast: Optional[str] = None
    max_allowed: Optional[int] = None
    base_limit: Optional[int] = None


@dataclass
class VisibilityRule:
    face_down_objects: Dict[str, Any] = field(default_factory=dict)
    hidden_zones: List[Dict[str, Any]] = field(default_factory=list)
    random_selection: bool = False

@dataclass
class ActivatedAbility:
    cost: List[Any]                 # parsed cost objects
    effect: List[Any]               # parsed effect objects
    is_mana_ability: bool = False
    restrictions: List[str] = field(default_factory=list)
    timing: str = "instant"

# ------------------------------------------------------------
# AXIS 2 CARD ROOT OBJECT
# ------------------------------------------------------------

@dataclass
class Axis2Characteristics:
    mana_cost: Optional["ManaCost"] = None
    mana_value: Optional[float] = None

    colors: List[str] = field(default_factory=list)
    color_identity: List[str] = field(default_factory=list)
    color_indicator: List[str] = field(default_factory=list)

    # IMPORTANT: layer system expects `.types`, not `.card_types`
    types: List[str] = field(default_factory=list)
    supertypes: List[str] = field(default_factory=list)
    subtypes: List[str] = field(default_factory=list)

    power: Optional[int] = None
    toughness: Optional[int] = None
    loyalty: Optional[int] = None
    defense: Optional[int] = None

    
@dataclass
class Axis2Card:
    characteristics: Axis2Characteristics
    actions: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Trigger] = field(default_factory=list)
    zone_permissions: ZonePermissions = field(default_factory=ZonePermissions)
    global_restrictions: List[GlobalRestriction] = field(default_factory=list)
    conditions: List[Condition] = field(default_factory=list)
    action_replacements: List[ActionReplacement] = field(default_factory=list)
    action_preventions: List[ActionPrevention] = field(default_factory=list)
    action_modifiers: List[ActionModifier] = field(default_factory=list)
    mandatory_actions: List[MandatoryAction] = field(default_factory=list)
    choice_constraints: List[str] = field(default_factory=list)
    limits: List[LimitRule] = field(default_factory=list)
    visibility_constraints: VisibilityRule = field(default_factory=VisibilityRule)
    keywords: List[str] = field(default_factory=list)
    static_effects: List[StaticEffect] = field(default_factory=list)
    replacement_effects: List[ReplacementEffect] = field(default_factory=list)
    modes: List[Mode] = field(default_factory=list)
    mode_choice: Optional[str] = None
    targeting_rules: TargetingRules = field(default_factory=TargetingRules)
    state_restrictions: List[str] = field(default_factory=list)
    turn_permissions: TurnPermissions = field(default_factory=TurnPermissions)
    dynamic_limit_conditions: List[Dict[str, Any]] = field(default_factory=list)
    conditional_usage: List[Dict[str, Any]] = field(default_factory=list)
    activated_abilities: List[ActivatedAbility] = field(default_factory=list)
