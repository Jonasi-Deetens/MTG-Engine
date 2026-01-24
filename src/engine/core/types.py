"""Type definitions and enums for the MTG engine."""

from __future__ import annotations

from enum import Enum
from typing import Literal


class Zone(str, Enum):
    """Game zones where objects can exist."""

    LIBRARY = "library"
    HAND = "hand"
    BATTLEFIELD = "battlefield"
    GRAVEYARD = "graveyard"
    EXILE = "exile"
    COMMAND = "command"
    STACK = "stack"


# String constants for backward compatibility
ZONE_LIBRARY = Zone.LIBRARY.value
ZONE_HAND = Zone.HAND.value
ZONE_BATTLEFIELD = Zone.BATTLEFIELD.value
ZONE_GRAVEYARD = Zone.GRAVEYARD.value
ZONE_EXILE = Zone.EXILE.value
ZONE_COMMAND = Zone.COMMAND.value
ZONE_STACK = Zone.STACK.value


class EventType(str, Enum):
    """Event types that can be published through the event bus."""

    # Zone transitions
    ENTERS_BATTLEFIELD = "enters_battlefield"
    LEAVES_BATTLEFIELD = "leaves_battlefield"
    CARD_ENTERS = "card_enters"
    DIES = "dies"

    # Spell/ability events
    SPELL_CAST = "spell_cast"
    SPELL_RESOLVED = "spell_resolved"
    SPELL_FIZZLED = "spell_fizzled"
    ABILITY_ACTIVATED = "ability_activated"
    ABILITY_RESOLVED = "ability_resolved"

    # Combat events
    ATTACKS = "attacks"
    BLOCKS = "blocks"
    COMBAT_DAMAGE_DEALT = "combat_damage_dealt"

    # Targeting events
    BECOMES_TARGET = "becomes_target"

    # Life/damage events
    LIFE_GAINED = "life_gained"
    LIFE_LOST = "life_lost"
    DAMAGE_DEALT = "damage_dealt"
    DEALS_DAMAGE = "deals_damage"
    TAKES_DAMAGE = "takes_damage"

    # Card draw
    CARD_DRAWN = "card_drawn"

    # Turn events
    TURN_BEGIN = "turn_begin"
    TURN_END = "turn_end"
    PHASE_BEGIN = "phase_begin"
    PHASE_END = "phase_end"
    STEP_BEGIN = "step_begin"
    STEP_END = "step_end"

    # Counter events
    COUNTER_ADDED = "counter_added"
    COUNTER_REMOVED = "counter_removed"


class StackItemKind(str, Enum):
    """Types of items that can be on the stack."""

    SPELL = "spell"
    ACTIVATED_ABILITY = "activated_ability"
    TRIGGERED_ABILITY = "triggered_ability"
    EFFECT_GRAPH = "effect_graph"


# Type alias for backward compatibility with Literal type
StackItemKindLiteral = Literal["spell", "activated_ability", "triggered_ability", "effect_graph"]


class Phase(str, Enum):
    """Game phases."""

    BEGINNING = "beginning"
    PRECOMBAT_MAIN = "precombat_main"
    COMBAT = "combat"
    POSTCOMBAT_MAIN = "postcombat_main"
    ENDING = "ending"


class Step(str, Enum):
    """Game steps within phases."""

    # Beginning phase
    UNTAP = "untap"
    UPKEEP = "upkeep"
    DRAW = "draw"

    # Main phases (no steps, but we use a placeholder)
    MAIN = "main"

    # Combat phase
    BEGINNING_OF_COMBAT = "beginning_of_combat"
    DECLARE_ATTACKERS = "declare_attackers"
    DECLARE_BLOCKERS = "declare_blockers"
    COMBAT_DAMAGE = "combat_damage"
    END_OF_COMBAT = "end_of_combat"

    # Ending phase
    END = "end"
    CLEANUP = "cleanup"
