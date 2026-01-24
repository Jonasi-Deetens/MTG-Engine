from __future__ import annotations

from typing import Optional

from .state import GameState, ResolveContext


def apply_splice_choices(
    game_state: GameState,
    player_id: int,
    effect_graph: Optional[dict],
    context: ResolveContext,
) -> None:
    if not effect_graph or not isinstance(context.choices, dict):
        return
    # Splice is not modeled in unified effect graphs yet.
    return

