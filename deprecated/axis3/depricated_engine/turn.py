# src/axis3/engine/turn.py

from __future__ import annotations

from typing import Tuple

from axis3.state.game_state import GameState, Phase, Step


_STEP_ORDER = [
    (Phase.BEGINNING, Step.UNTAP),
    (Phase.BEGINNING, Step.UPKEEP),
    (Phase.BEGINNING, Step.DRAW),
    (Phase.PRECOMBAT_MAIN, Step.DRAW),         # dummy step name; we only care about phase
    (Phase.COMBAT, Step.BEGIN_COMBAT),
    (Phase.COMBAT, Step.DECLARE_ATTACKERS),
    (Phase.COMBAT, Step.DECLARE_BLOCKERS),
    (Phase.COMBAT, Step.COMBAT_DAMAGE),
    (Phase.COMBAT, Step.END_COMBAT),
    (Phase.POSTCOMBAT_MAIN, Step.DRAW),        # dummy step
    (Phase.ENDING, Step.END_STEP),
    (Phase.ENDING, Step.CLEANUP),
]


def _current_index(game_state: GameState) -> int:
    ts = game_state.turn
    for i, (phase, step) in enumerate(_STEP_ORDER):
        if phase == ts.phase and step == ts.step:
            return i
    raise ValueError(f"Invalid phase/step combination: {ts.phase}, {ts.step}")


def advance_step(game_state: GameState) -> None:
    """
    Move to the next step/phase in the turn, or start a new turn if at end of cleanup.
    """
    idx = _current_index(game_state)
    if idx == len(_STEP_ORDER) - 1:
        _start_next_turn(game_state)
        return

    next_phase, next_step = _STEP_ORDER[idx + 1]
    ts = game_state.turn
    ts.phase = next_phase
    ts.step = next_step

    # Priority always starts with active player at beginning of each step
    ts.priority_player = ts.active_player
    ts.stack_empty_since_last_priority = True


def _start_next_turn(game_state: GameState) -> None:
    """
    Increment turn number, rotate active player, and go to the first step.
    """
    ts = game_state.turn
    ts.turn_number += 1
    ts.active_player = (ts.active_player + 1) % len(game_state.players)
    ts.priority_player = ts.active_player
    ts.phase, ts.step = _STEP_ORDER[0]
    ts.stack_empty_since_last_priority = True
