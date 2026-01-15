from __future__ import annotations

from typing import Any, Dict, Optional

from .state import GameState, ResolveContext, GameObject


def resolve_player_id(context: ResolveContext, fallback_controller_id: Optional[int]) -> Optional[int]:
    if "player_id" in context.targets:
        return context.targets["player_id"]
    if "target_player" in context.targets:
        return context.targets["target_player"]
    if "player" in context.targets:
        return context.targets["player"]
    return fallback_controller_id


def resolve_object_id(context: ResolveContext, key: str, fallback: Optional[str]) -> Optional[str]:
    if key in context.targets:
        return context.targets[key]
    if "target" in context.targets:
        return context.targets["target"]
    return fallback


def resolve_object(
    game_state: GameState,
    context: ResolveContext,
    target_key: str,
    fallback: Optional[str],
) -> Optional[GameObject]:
    obj_id = resolve_object_id(context, target_key, fallback)
    if obj_id:
        return game_state.objects.get(obj_id)
    return None
