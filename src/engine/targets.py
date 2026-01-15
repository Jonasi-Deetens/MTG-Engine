from __future__ import annotations

from typing import Any, Dict, Optional, List

from .state import GameState, ResolveContext, GameObject
from .zones import ZONE_BATTLEFIELD


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


def validate_targets(game_state: GameState, context: ResolveContext) -> None:
    if not has_legal_targets(game_state, context):
        raise ValueError("No legal targets.")


def get_target_issues(game_state: GameState, context: ResolveContext) -> List[str]:
    issues: List[str] = []
    targets = context.targets

    target_id = targets.get("target")
    target_list = targets.get("targets") if isinstance(targets.get("targets"), list) else None
    if target_id:
        ok, reason = _check_object_target(game_state, context, target_id)
        if not ok and reason:
            issues.append(f"{target_id}: {reason}")
    if target_list is not None and not any(_is_legal_object_target(game_state, context, target) for target in target_list):
        issues.append("No legal object targets.")

    target_player = targets.get("target_player")
    player_list = targets.get("target_players") if isinstance(targets.get("target_players"), list) else None
    if target_player is not None and not _is_legal_player_target(game_state, target_player):
        issues.append(f"Player {target_player}: illegal target.")
    if player_list is not None and not any(_is_legal_player_target(game_state, player_id) for player_id in player_list):
        issues.append("No legal player targets.")

    spell_target = targets.get("spell_target")
    spell_list = targets.get("spell_targets") if isinstance(targets.get("spell_targets"), list) else None
    if spell_target is not None and not _is_legal_spell_target(game_state, spell_target):
        issues.append(f"Spell {spell_target}: not on the stack.")
    if spell_list is not None and not any(_is_legal_spell_target(game_state, target_id) for target_id in spell_list):
        issues.append("No legal spell targets.")

    return issues


def normalize_targets(game_state: GameState, context: ResolveContext) -> None:
    targets = context.targets
    if isinstance(targets.get("targets"), list):
        legal = [target_id for target_id in targets["targets"] if _is_legal_object_target(game_state, context, target_id)]
        targets["targets"] = legal
        if "target" not in targets and legal:
            targets["target"] = legal[0]
    if isinstance(targets.get("target_players"), list):
        legal_players = [player_id for player_id in targets["target_players"] if _is_legal_player_target(game_state, player_id)]
        targets["target_players"] = legal_players
        if "target_player" not in targets and legal_players:
            targets["target_player"] = legal_players[0]

    if isinstance(targets.get("spell_targets"), list):
        legal_spells = [target_id for target_id in targets["spell_targets"] if _is_legal_spell_target(game_state, target_id)]
        targets["spell_targets"] = legal_spells
        if "spell_target" not in targets and legal_spells:
            targets["spell_target"] = legal_spells[0]


def has_legal_targets(game_state: GameState, context: ResolveContext) -> bool:
    targets = context.targets
    target_id = targets.get("target")
    target_list = targets.get("targets") if isinstance(targets.get("targets"), list) else None
    if target_id and not _is_legal_object_target(game_state, context, target_id):
        return False
    if target_list is not None and not any(_is_legal_object_target(game_state, context, target) for target in target_list):
        return False

    target_player = targets.get("target_player")
    player_list = targets.get("target_players") if isinstance(targets.get("target_players"), list) else None
    if target_player is not None and not _is_legal_player_target(game_state, target_player):
        return False
    if player_list is not None and not any(_is_legal_player_target(game_state, player_id) for player_id in player_list):
        return False

    spell_target = targets.get("spell_target")
    spell_list = targets.get("spell_targets") if isinstance(targets.get("spell_targets"), list) else None
    if spell_target is not None and not _is_legal_spell_target(game_state, spell_target):
        return False
    if spell_list is not None and not any(_is_legal_spell_target(game_state, target_id) for target_id in spell_list):
        return False

    return True


def _check_object_target(game_state: GameState, context: ResolveContext, target_id: str) -> tuple[bool, str | None]:
    obj = game_state.objects.get(target_id)
    if not obj:
        return False, "Target object not found."
    if obj.zone != ZONE_BATTLEFIELD:
        return False, "Target must be on the battlefield."
    if obj.phased_out:
        return False, "Target is phased out."
    if "Ward" in obj.keywords and not context.choices.get("ward_paid"):
        return False, "Ward cost not paid."
    if "Hexproof" in obj.keywords and context.controller_id is not None:
        if obj.controller_id != context.controller_id:
            return False, "Target has hexproof."
    if obj.protections and context.source_id:
        source = game_state.objects.get(context.source_id)
        if source and any(color in obj.protections for color in source.colors):
            return False, "Target has protection from source."
    return True, None


def _is_legal_object_target(game_state: GameState, context: ResolveContext, target_id: str) -> bool:
    return _check_object_target(game_state, context, target_id)[0]


def _is_legal_player_target(game_state: GameState, player_id: int) -> bool:
    return any(player.id == player_id for player in game_state.players)


def _is_legal_spell_target(game_state: GameState, target_id: str) -> bool:
    for item in game_state.stack.items:
        if item.kind != "spell":
            continue
        if item.payload.get("object_id") == target_id or item.payload.get("copy_of") == target_id:
            return True
    return False
