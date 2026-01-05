# axis3/state/registries.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Any


# ============================================================
# PERMISSIONS
# ============================================================

@dataclass
class PermissionRegistry:
    """
    Stores casting and activation permissions for runtime objects.
    Example permissions:
      - "may_cast_from_graveyard"
      - "may_cast_without_paying_mana_cost"
      - "may_activate_as_instant"
    """
    permissions: Dict[str, List[str]] = field(default_factory=dict)

    def grant(self, source_id: str, permission: str):
        self.permissions.setdefault(source_id, []).append(permission)

    def has(self, source_id: str, permission: str) -> bool:
        return permission in self.permissions.get(source_id, [])


# ============================================================
# ALTERNATIVE COSTS
# ============================================================

@dataclass
class AlternativeCost:
    tag: str
    cost: str


@dataclass
class AlternativeCostRegistry:
    """
    Stores alternative costs for spells.
    Example:
      - Flashback: tag="flashback", cost="{8}{W}{W}"
      - Escape: tag="escape", cost="{4}{G}{G}"
      - Overload: tag="overload", cost="{3}{U}{U}"
    """
    alt_costs: Dict[str, List[AlternativeCost]] = field(default_factory=dict)

    def add(self, source_id: str, tag: str, cost: str):
        self.alt_costs.setdefault(source_id, []).append(
            AlternativeCost(tag=tag, cost=cost)
        )

    def get(self, source_id: str) -> List[AlternativeCost]:
        return self.alt_costs.get(source_id, [])


# ============================================================
# COST REDUCTIONS
# ============================================================

@dataclass
class CostReductionRule:
    tag: str
    amount_fn: Callable[[Any, int], int]
    applies_if: Callable[[Any], bool]


@dataclass
class CostReductionRegistry:
    """
    Stores dynamic cost reduction rules.
    Example:
      - Flashback reduction
      - Convoke
      - Affinity
      - Improvise
      - Delve
    """
    reductions: Dict[str, List[CostReductionRule]] = field(default_factory=dict)

    def add(self, source_id: str, tag: str,
            amount_fn: Callable[[Any, int], int],
            applies_if: Callable[[Any], bool]):
        self.reductions.setdefault(source_id, []).append(
            CostReductionRule(tag, amount_fn, applies_if)
        )

    def get(self, source_id: str) -> List[CostReductionRule]:
        return self.reductions.get(source_id, [])


# ============================================================
# REPLACEMENT EFFECTS
# ============================================================

@dataclass
class ReplacementEffect:
    tag: str
    applies_if: Callable[[Any], bool]
    effect_fn: Callable[[Any, Any], Any]


@dataclass
class ReplacementEffectRegistry:
    """
    Stores replacement effects.
    Example:
      - Flashback: exile on resolution
      - Unearth: exile if it would leave the battlefield
      - Disturb: exile on resolution
      - Buyback: return to hand instead of graveyard
    """
    replacements: Dict[str, List[ReplacementEffect]] = field(default_factory=dict)

    def add(self, source_id: str, tag: str,
            applies_if: Callable[[Any], bool],
            effect_fn: Callable[[Any, Any], Any]):
        self.replacements.setdefault(source_id, []).append(
            ReplacementEffect(tag, applies_if, effect_fn)
        )

    def get(self, source_id: str) -> List[ReplacementEffect]:
        return self.replacements.get(source_id, [])


# ============================================================
# CONTINUOUS EFFECTS
# ============================================================

@dataclass
class ContinuousEffectRegistry:
    """
    Stores continuous effects that apply in layers.
    Example:
      - Anthem effects
      - Type-changing effects
      - Power/toughness modifications
      - Ability-granting effects
    """
    effects: List[Any] = field(default_factory=list)

    def add(self, effect: Any):
        self.effects.append(effect)

    def all(self) -> List[Any]:
        return self.effects


# ============================================================
# GLOBAL RESTRICTIONS
# ============================================================

@dataclass
class GlobalRestrictionRegistry:
    """
    Stores global restrictions such as:
      - "Players can't gain life"
      - "Creatures can't attack"
      - "Spells can't be countered"
    """
    restrictions: List[Any] = field(default_factory=list)

    def add(self, restriction: Any):
        self.restrictions.append(restriction)

    def all(self) -> List[Any]:
        return self.restrictions


# ============================================================
# MASTER CONTAINER
# ============================================================

@dataclass
class EffectRegistries:
    """
    Container for all effect-related registries.
    This keeps GameState clean and modular.
    """
    permissions: PermissionRegistry = field(default_factory=PermissionRegistry)
    alternative_costs: AlternativeCostRegistry = field(default_factory=AlternativeCostRegistry)
    cost_reductions: CostReductionRegistry = field(default_factory=CostReductionRegistry)
    replacement_effects: ReplacementEffectRegistry = field(default_factory=ReplacementEffectRegistry)
    continuous_effects: ContinuousEffectRegistry = field(default_factory=ContinuousEffectRegistry)
    global_restrictions: GlobalRestrictionRegistry = field(default_factory=GlobalRestrictionRegistry)
