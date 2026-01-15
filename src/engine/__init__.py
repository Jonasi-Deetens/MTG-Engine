"""Runtime MTG engine core and ability graph execution."""

from .state import GameState, GameObject, PlayerState, ResolveContext
from .turn import TurnState, Phase, Step
from .combat import CombatState
from .turn_manager import TurnManager
from .stack import Stack, StackItem
from .events import Event, EventBus
from .priority import PriorityManager
from .ability_graph import AbilityGraphRuntimeAdapter
from .ability_registry import AbilityRegistry
from .commander import register_commander, apply_commander_tax, record_commander_damage

__all__ = [
    "AbilityGraphRuntimeAdapter",
    "AbilityRegistry",
    "Event",
    "EventBus",
    "GameObject",
    "GameState",
    "PlayerState",
    "PriorityManager",
    "ResolveContext",
    "Stack",
    "StackItem",
    "TurnManager",
    "TurnState",
    "Phase",
    "Step",
    "CombatState",
    "register_commander",
    "apply_commander_tax",
    "record_commander_damage",
]
