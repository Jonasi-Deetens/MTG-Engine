from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from .combat import CombatState


class Phase(str, Enum):
    BEGINNING = "beginning"
    PRECOMBAT_MAIN = "precombat_main"
    COMBAT = "combat"
    POSTCOMBAT_MAIN = "postcombat_main"
    ENDING = "ending"


class Step(str, Enum):
    UNTAP = "untap"
    UPKEEP = "upkeep"
    DRAW = "draw"
    PRECOMBAT_MAIN = "precombat_main"
    BEGIN_COMBAT = "begin_combat"
    DECLARE_ATTACKERS = "declare_attackers"
    DECLARE_BLOCKERS = "declare_blockers"
    COMBAT_DAMAGE = "combat_damage"
    END_COMBAT = "end_combat"
    POSTCOMBAT_MAIN = "postcombat_main"
    END = "end"
    CLEANUP = "cleanup"


PHASE_STEP_ORDER: List[Tuple[Phase, Step]] = [
    (Phase.BEGINNING, Step.UNTAP),
    (Phase.BEGINNING, Step.UPKEEP),
    (Phase.BEGINNING, Step.DRAW),
    (Phase.PRECOMBAT_MAIN, Step.PRECOMBAT_MAIN),
    (Phase.COMBAT, Step.BEGIN_COMBAT),
    (Phase.COMBAT, Step.DECLARE_ATTACKERS),
    (Phase.COMBAT, Step.DECLARE_BLOCKERS),
    (Phase.COMBAT, Step.COMBAT_DAMAGE),
    (Phase.COMBAT, Step.END_COMBAT),
    (Phase.POSTCOMBAT_MAIN, Step.POSTCOMBAT_MAIN),
    (Phase.ENDING, Step.END),
    (Phase.ENDING, Step.CLEANUP),
]


@dataclass
class TurnState:
    turn_number: int = 1
    active_player_index: int = 0
    phase: Phase = Phase.BEGINNING
    step: Step = Step.UNTAP
    land_plays_this_turn: int = 0
    combat_state: Optional[CombatState] = None
    priority_current_index: int = 0
    priority_pass_count: int = 0
    priority_last_passed_player_id: Optional[int] = None
