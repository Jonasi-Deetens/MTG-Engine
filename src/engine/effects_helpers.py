from __future__ import annotations

from typing import Any, Dict, List, Optional

from .state import GameState, ResolveContext, GameObject
from .targets import resolve_object, resolve_object_id, resolve_player_id, is_overloaded, is_legal_object_target

ANY_TARGET_TYPES = {"Creature", "Planeswalker", "Battle"}


def _is_any_target_object(obj: GameObject) -> bool:
    return any(card_type in (obj.types or []) for card_type in ANY_TARGET_TYPES)


def resolve_target_object(game_state: GameState, context: ResolveContext, target_key: str) -> Optional[GameObject]:
    fallback = context.source_id if target_key in ("self", "source") else None
    obj = resolve_object(game_state, context, target_key, fallback)
    if obj and not is_overloaded(context):
        if target_key in ("any", "target") and not _is_any_target_object(obj):
            return None
        if not is_legal_object_target(game_state, context, obj.id):
            return None
    return obj


def resolve_target_objects(game_state: GameState, context: ResolveContext, target_key: str) -> List[GameObject]:
    targets: List[GameObject] = []
    if target_key.startswith("target_") and (target_key.endswith("_you_control") or target_key.endswith("_opponents_control")):
        controller_id = context.controller_id
        if controller_id is None:
            return []
        scope = "you_control" if target_key.endswith("_you_control") else "opponent_control"
        base_key = target_key.replace("_you_control", "").replace("_opponents_control", "")
        primary = resolve_target_object(game_state, context, base_key)
        if primary:
            if scope == "you_control" and primary.controller_id != controller_id:
                return []
            if scope == "opponent_control" and primary.controller_id == controller_id:
                return []
            targets.append(primary)
        for obj_id in context.targets.get("targets", []) if isinstance(context.targets.get("targets"), list) else []:
            obj = game_state.objects.get(obj_id)
            if not obj:
                continue
            if scope == "you_control" and obj.controller_id != controller_id:
                continue
            if scope == "opponent_control" and obj.controller_id == controller_id:
                continue
            if obj not in targets:
                targets.append(obj)
        return targets
    if target_key in (
        "permanents_you_control",
        "creatures_you_control",
        "artifacts_you_control",
        "enchantments_you_control",
        "planeswalkers_you_control",
        "lands_you_control",
        "permanents_opponents_control",
        "creatures_opponents_control",
        "artifacts_opponents_control",
        "enchantments_opponents_control",
        "planeswalkers_opponents_control",
        "lands_opponents_control",
        "you_control",
        "opponent_control",
    ):
        controller_id = context.controller_id
        if controller_id is None:
            return []
        def matches(obj: GameObject) -> bool:
            if obj.zone != "battlefield" or obj.phased_out:
                return False
            is_controller = obj.controller_id == controller_id
            if target_key.endswith("_you_control") or target_key == "you_control":
                if not is_controller:
                    return False
            if target_key.endswith("_opponents_control") or target_key == "opponent_control":
                if is_controller:
                    return False
            if target_key.startswith("creatures_") and "Creature" not in obj.types:
                return False
            if target_key.startswith("artifacts_") and "Artifact" not in obj.types:
                return False
            if target_key.startswith("enchantments_") and "Enchantment" not in obj.types:
                return False
            if target_key.startswith("planeswalkers_") and "Planeswalker" not in obj.types:
                return False
            if target_key.startswith("lands_") and "Land" not in obj.types:
                return False
            return True
        return [obj for obj in game_state.objects.values() if matches(obj)]
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
            if target_key in ("any", "target") and not _is_any_target_object(obj):
                continue
            if not is_overloaded(context) and not is_legal_object_target(game_state, context, obj_id):
                continue
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
    if target_key in ("each_player", "all_players"):
        return [player.id for player in game_state.players if not getattr(player, "removed_from_game", False)]
    if target_key in ("each_opponent", "opponents"):
        controller_id = context.controller_id if context.controller_id is not None else fallback_controller_id
        if controller_id is None:
            return []
        return [
            player.id
            for player in game_state.players
            if player.id != controller_id and not getattr(player, "removed_from_game", False)
        ]
    if target_key == "opponent":
        explicit = resolve_target_players(context, None, game_state)
        if explicit:
            return explicit
        controller_id = context.controller_id if context.controller_id is not None else fallback_controller_id
        if controller_id is None:
            return []
        return [
            player.id
            for player in game_state.players
            if player.id != controller_id and not getattr(player, "removed_from_game", False)
        ]
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
        "aura": "Aura",
        "equipment": "Equipment",
        "land": "Land",
        "planeswalker": "Planeswalker",
        "instant": "Instant",
        "sorcery": "Sorcery",
        "battle": "Battle",
        "tribal": "Tribal",
        "legendary": "Legendary",
    }
    return mapping.get(lowered, value)

