from __future__ import annotations

from typing import Any, Dict, List, Optional

from .state import GameState, ResolveContext, GameObject
from .targets import resolve_object, resolve_object_id, resolve_player_id, is_overloaded


def resolve_target_object(game_state: GameState, context: ResolveContext, target_key: str) -> Optional[GameObject]:
    fallback = context.source_id if target_key in ("self", "source") else None
    return resolve_object(game_state, context, target_key, fallback)


def resolve_target_objects(game_state: GameState, context: ResolveContext, target_key: str) -> List[GameObject]:
    targets: List[GameObject] = []
    if is_overloaded(context):
        overload_key = target_key
        if overload_key in ("any", "target"):
            overload_key = "target_permanent"
        elif overload_key == "permanent":
            overload_key = "target_permanent"
        elif overload_key == "creature":
            overload_key = "target_creature"
        elif overload_key == "artifact":
            overload_key = "target_artifact"
        elif overload_key == "enchantment":
            overload_key = "target_enchantment"
        elif overload_key == "planeswalker":
            overload_key = "target_planeswalker"
        if overload_key.startswith("target_"):
            for obj in game_state.objects.values():
                if obj.zone != "battlefield" or obj.phased_out:
                    continue
                if overload_key == "target_permanent":
                    targets.append(obj)
                elif overload_key == "target_creature" and "Creature" in obj.types:
                    targets.append(obj)
                elif overload_key == "target_artifact" and "Artifact" in obj.types:
                    targets.append(obj)
                elif overload_key == "target_enchantment" and "Enchantment" in obj.types:
                    targets.append(obj)
                elif overload_key == "target_planeswalker" and "Planeswalker" in obj.types:
                    targets.append(obj)
            return targets
    primary = resolve_target_object(game_state, context, target_key)
    if primary:
        targets.append(primary)
    for obj_id in context.targets.get("targets", []) if isinstance(context.targets.get("targets"), list) else []:
        obj = game_state.objects.get(obj_id)
        if obj and obj not in targets:
            targets.append(obj)
    return targets


def resolve_target_players(
    context: ResolveContext,
    fallback_controller_id: Optional[int],
    game_state: Optional[GameState] = None,
) -> List[int]:
    players: List[int] = []
    if is_overloaded(context) and game_state is not None:
        return [player.id for player in game_state.players if not getattr(player, "removed_from_game", False)]
    primary = resolve_player_id(context, fallback_controller_id)
    if primary is not None:
        players.append(primary)
    for player_id in context.targets.get("target_players", []) if isinstance(context.targets.get("target_players"), list) else []:
        if player_id not in players:
            players.append(player_id)
    return players


def resolve_effect_players(
    game_state: GameState,
    context: ResolveContext,
    effect: Dict[str, Any],
    fallback_controller_id: Optional[int],
) -> List[int]:
    target_key = effect.get("target", "player")
    if is_overloaded(context) and target_key in ("player", "any"):
        return [player.id for player in game_state.players if not getattr(player, "removed_from_game", False)]
    return resolve_target_players(context, fallback_controller_id, game_state)


def resolve_choice_for_player(choices: Any, key: str, player_id: int, fallback: Any = None) -> Any:
    if not isinstance(choices, dict):
        return fallback
    player_map = choices.get(f"{key}_by_player")
    if isinstance(player_map, dict):
        if str(player_id) in player_map:
            return player_map.get(str(player_id))
        if player_id in player_map:
            return player_map.get(player_id)
    return choices.get(key, fallback)


def resolve_target_list_for_player(context: ResolveContext, key: str, player_id: int) -> List[Any]:
    targets = context.targets or {}
    player_map = targets.get(f"{key}_by_player")
    if isinstance(player_map, dict):
        if str(player_id) in player_map:
            return list(player_map.get(str(player_id)) or [])
        if player_id in player_map:
            return list(player_map.get(player_id) or [])
    value = targets.get(key, [])
    return list(value) if isinstance(value, list) else []


def resolve_enter_choice_value(game_state: GameState, context: ResolveContext, choice_key: str) -> Optional[str]:
    choices = context.choices or {}
    enter_choices = choices.get("enter_choices") if isinstance(choices, dict) else None
    if isinstance(enter_choices, dict):
        value = enter_choices.get(choice_key)
        if value:
            return value
    source_id = context.source_id
    if source_id:
        obj = game_state.objects.get(source_id)
        if obj and getattr(obj, "etb_choices", None):
            value = obj.etb_choices.get(choice_key)
            if value:
                return value
    return None


def normalize_card_type(value: str) -> str:
    lowered = value.strip().lower()
    mapping = {
        "creature": "Creature",
        "artifact": "Artifact",
        "enchantment": "Enchantment",
        "land": "Land",
        "planeswalker": "Planeswalker",
        "instant": "Instant",
        "sorcery": "Sorcery",
        "battle": "Battle",
        "tribal": "Tribal",
        "legendary": "Legendary",
    }
    return mapping.get(lowered, value)

