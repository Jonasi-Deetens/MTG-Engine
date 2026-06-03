"""Core data models for the MTG engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class GameObject:
    """Represents a game object (card, token, etc.)."""

    id: str
    name: str
    owner_id: int
    controller_id: int
    types: List[str]
    zone: str
    mana_cost: Optional[str] = None
    base_name: Optional[str] = None
    base_mana_cost: Optional[str] = None
    base_mana_value: Optional[int] = None
    base_types: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    base_colors: List[str] = field(default_factory=list)
    type_line: Optional[str] = None
    base_type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    base_oracle_text: Optional[str] = None
    mana_value: Optional[int] = None
    power: Optional[int] = None
    toughness: Optional[int] = None
    base_power: Optional[int] = None
    base_toughness: Optional[int] = None
    cda_power: Optional[int] = None
    cda_toughness: Optional[int] = None
    base_keywords: Set[str] = field(default_factory=set)
    entered_turn: Optional[int] = None
    tapped: bool = False
    damage: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    keywords: Set[str] = field(default_factory=set)
    protections: Set[str] = field(default_factory=set)
    attached_to: Optional[str] = None
    is_token: bool = False
    was_cast: bool = False
    is_attacking: bool = False
    is_blocking: bool = False
    phased_out: bool = False
    transformed: bool = False
    regenerate_shield: bool = False
    temporary_effects: List[Dict[str, Any]] = field(default_factory=list)
    effect_graphs: List[Dict[str, Any]] = field(default_factory=list)
    base_effect_graphs: List[Dict[str, Any]] = field(default_factory=list)
    activation_limits: Dict[str, int] = field(default_factory=dict)
    etb_choices: Dict[str, Any] = field(default_factory=dict)
    base_etb_choices: Dict[str, Any] = field(default_factory=dict)
    base_controller_id: Optional[int] = None


@dataclass
class PlayerState:
    """Represents a player's state."""

    id: int
    life: int = 40
    max_hand_size: int = 7
    has_lost: bool = False
    removed_from_game: bool = False
    poison_counters: int = 0
    mana_pool: Dict[str, int] = field(default_factory=dict)
    library: List[str] = field(default_factory=list)
    hand: List[str] = field(default_factory=list)
    graveyard: List[str] = field(default_factory=list)
    exile: List[str] = field(default_factory=list)
    command: List[str] = field(default_factory=list)
    battlefield: List[str] = field(default_factory=list)
    commander_id: Optional[str] = None
    commander_tax: int = 0
    commander_damage_taken: Dict[str, int] = field(default_factory=dict)

    def total_mana(self) -> int:
        """Get total mana in pool."""
        return sum(self.mana_pool.values())


@dataclass
class ResolveContext:
    """Context for resolving spells and abilities."""

    source_id: Optional[str] = None
    controller_id: Optional[int] = None
    triggering_source_id: Optional[str] = None
    triggering_aura_id: Optional[str] = None
    triggering_spell_id: Optional[str] = None
    targets: Dict[str, Any] = field(default_factory=dict)
    targets_by_effect: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required_targets_by_effect: Dict[str, List[str]] = field(default_factory=dict)
    distinct_targets_by_effect: Dict[str, List[str]] = field(default_factory=dict)
    min_targets_by_effect: Dict[str, Dict[str, int]] = field(default_factory=dict)
    choices: Dict[str, Any] = field(default_factory=dict)
    previous_results: List[Dict[str, Any]] = field(default_factory=list)
