from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from api.schemas.unified_effect_schemas import Initiation
from ..zones import ZONE_BATTLEFIELD
from .active_effects import ActiveEffect
from .normalize import normalize_graph
if TYPE_CHECKING:
    from ..state import GameObject, GameState


def register_active_effects_from_object(game_state: GameState, obj: GameObject) -> None:
    for raw_graph in obj.effect_graphs:
        if not isinstance(raw_graph, dict) or "steps" not in raw_graph:
            continue
        try:
            graph = normalize_graph(raw_graph)
        except ValueError:
            continue

        for step in graph.steps:
            effect = step.effect
            if not _should_register(effect, obj):
                continue
            active = ActiveEffect(
                effect_id=effect.id,
                source_id=obj.id,
                controller_id=obj.controller_id,
                effect_data=effect,
                timestamp=obj.entered_turn or game_state.turn.turn_number,
                timestamp_order=_next_effect_order(game_state),
                effect_graph=graph,
                step_id=step.id,
            )
            game_state.active_effect_registry.register(active)


def unregister_active_effects_for_source(game_state: GameState, source_id: str) -> None:
    game_state.active_effect_registry.unregister_by_source(source_id)


def _should_register(effect, obj: GameObject) -> bool:
    if effect.initiation == Initiation.TRIGGERED:
        trigger = getattr(effect, "trigger", None)
        event = getattr(trigger, "event", None) if trigger else None
        if event in ("enters_battlefield", "card_enters") and obj.zone != ZONE_BATTLEFIELD:
            return False
        return True
    body_kind = getattr(effect.effect, "kind", None)
    if body_kind in ("continuous", "replacement", "prevention"):
        return True
    return False


def _next_effect_order(game_state: GameState) -> int:
    game_state.effect_timestamp_counter += 1
    return game_state.effect_timestamp_counter
