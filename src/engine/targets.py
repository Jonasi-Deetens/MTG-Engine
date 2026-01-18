from __future__ import annotations

from typing import Any, Dict, Optional, List

from .state import GameState, ResolveContext, GameObject
from .costs import parse_ward_keywords
from .mana import can_pay_cost, can_pay_cost_with_payment, parse_mana_cost, pay_cost, pay_cost_with_payment
from .zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD


def resolve_player_id(context: ResolveContext, fallback_controller_id: Optional[int]) -> Optional[int]:
    if "player_id" in context.targets:
        return context.targets["player_id"]
    if "target_player" in context.targets:
        return context.targets["target_player"]
    if "player" in context.targets:
        return context.targets["player"]
    return fallback_controller_id


def is_overloaded(context: ResolveContext) -> bool:
    if not isinstance(context.choices, dict):
        return False
    tag = context.choices.get("alternative_cost_tag", "")
    return isinstance(tag, str) and tag.startswith("overload")


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
    if is_overloaded(context):
        return
    if not has_legal_targets(game_state, context):
        raise ValueError("No legal targets.")


def get_target_issues(game_state: GameState, context: ResolveContext) -> List[str]:
    if is_overloaded(context):
        return []
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
    if is_overloaded(context):
        return
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
    if is_overloaded(context):
        return True
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
    if "Shroud" in obj.keywords:
        return False, "Target has shroud."
    if "Hexproof" in obj.keywords and context.controller_id is not None:
        if obj.controller_id != context.controller_id:
            return False, "Target has hexproof."
    source_id = (
        context.source_id
        or context.triggering_source_id
        or context.triggering_spell_id
        or context.triggering_aura_id
    )
    if obj.protections and source_id:
        source = game_state.objects.get(source_id)
        if source and any(color in obj.protections for color in source.colors):
            return False, "Target has protection from source."
    return True, None


def _collect_target_ids(context: ResolveContext) -> List[str]:
    targets = []
    target_id = context.targets.get("target")
    if target_id:
        targets.append(target_id)
    extra = context.targets.get("targets")
    if isinstance(extra, list):
        for obj_id in extra:
            if obj_id not in targets:
                targets.append(obj_id)
    return targets


def _ward_cost_entries(obj: GameObject) -> List[Dict[str, Any]]:
    return parse_ward_keywords(obj.keywords)


def enforce_ward_payment(game_state: GameState, context: ResolveContext) -> None:
    target_ids = _collect_target_ids(context)
    if not target_ids:
        return
    ward_payments = context.choices.get("ward_payments") if isinstance(context.choices, dict) else {}
    auto_pay = bool(context.choices.get("ward_auto_pay")) if isinstance(context.choices, dict) else False
    controller_id = context.controller_id
    if controller_id is None:
        return
    for obj_id in target_ids:
        obj = game_state.objects.get(obj_id)
        if not obj:
            continue
        costs = _ward_cost_entries(obj)
        if not costs:
            continue
        for index, cost in enumerate(costs):
            entry: Dict[str, Any] = {}
            if isinstance(ward_payments, dict) and obj_id in ward_payments:
                provided = ward_payments.get(obj_id) or {}
                if isinstance(provided, list) and index < len(provided):
                    entry = provided[index] or {}
                elif isinstance(provided, dict):
                    entry = provided
            if cost.get("type") == "mana":
                mana_cost = parse_mana_cost(cost.get("cost"), x_value=0)
                payment = entry.get("mana_payment")
                payment_detail = entry.get("mana_payment_detail")
                if payment is not None:
                    if not can_pay_cost_with_payment(
                        game_state.get_player(controller_id).mana_pool,
                        mana_cost,
                        payment,
                        payment_detail,
                    ):
                        raise ValueError("Not enough mana to pay ward cost.")
                    pay_cost_with_payment(game_state, controller_id, mana_cost, payment, payment_detail)
                    continue
                if auto_pay:
                    if not can_pay_cost(game_state.get_player(controller_id).mana_pool, mana_cost):
                        raise ValueError("Not enough mana to pay ward cost.")
                    pay_cost(game_state, controller_id, mana_cost)
                    continue
                raise ValueError("Ward cost not paid.")
            if cost.get("type") == "life":
                amount = int(cost.get("amount", 0))
                if amount <= 0:
                    continue
                if not auto_pay and entry.get("life_payment") is None:
                    raise ValueError("Ward cost not paid.")
                player = game_state.get_player(controller_id)
                if player.life < amount:
                    raise ValueError("Not enough life to pay ward cost.")
                player.life -= amount
                continue
            if cost.get("type") == "discard":
                amount = int(cost.get("amount", 1))
                discard_ids = entry.get("discard_ids")
                discard_id = entry.get("discard_id")
                if discard_ids is None and discard_id:
                    discard_ids = [discard_id]
                if not isinstance(discard_ids, list) or len(discard_ids) != amount:
                    raise ValueError("Ward cost not paid.")
                player = game_state.get_player(controller_id)
                for card_id in discard_ids:
                    if card_id not in player.hand:
                        raise ValueError("Invalid card selected to discard for ward.")
                    game_state.move_object(card_id, ZONE_GRAVEYARD)
                continue
            if cost.get("type") == "sacrifice":
                sacrifice_id = entry.get("sacrifice_id")
                if not sacrifice_id:
                    raise ValueError("Ward cost not paid.")
                sacrifice_obj = game_state.objects.get(sacrifice_id)
                if not sacrifice_obj or sacrifice_obj.controller_id != controller_id:
                    raise ValueError("Invalid permanent selected to sacrifice for ward.")
                if sacrifice_obj.zone != ZONE_BATTLEFIELD:
                    raise ValueError("Selected permanent is not on the battlefield.")
                card_type = cost.get("card_type")
                if card_type and card_type.capitalize() not in (sacrifice_obj.types or []):
                    raise ValueError("Selected permanent does not match ward sacrifice cost.")
                if cost.get("nonland") and "Land" in (sacrifice_obj.types or []):
                    raise ValueError("Selected permanent does not match ward sacrifice cost.")
                game_state.sacrifice_object(sacrifice_id)
                continue
            if cost.get("type") == "tap":
                tap_id = entry.get("tap_id")
                if not tap_id:
                    raise ValueError("Ward cost not paid.")
                tap_obj = game_state.objects.get(tap_id)
                if not tap_obj or tap_obj.controller_id != controller_id:
                    raise ValueError("Invalid permanent selected to tap for ward.")
                if tap_obj.zone != ZONE_BATTLEFIELD or tap_obj.tapped:
                    raise ValueError("Selected permanent is not an untapped permanent.")
                card_type = cost.get("card_type")
                if card_type and card_type.capitalize() not in (tap_obj.types or []):
                    raise ValueError("Selected permanent does not match ward tap cost.")
                if cost.get("nonland") and "Land" in (tap_obj.types or []):
                    raise ValueError("Selected permanent does not match ward tap cost.")
                tap_obj.tapped = True
                continue
            raise ValueError("Ward cost not paid.")


def _is_legal_object_target(game_state: GameState, context: ResolveContext, target_id: str) -> bool:
    return _check_object_target(game_state, context, target_id)[0]


def _is_legal_player_target(game_state: GameState, player_id: int) -> bool:
    return any(player.id == player_id and not getattr(player, "removed_from_game", False) for player in game_state.players)


def _is_legal_spell_target(game_state: GameState, target_id: str) -> bool:
    for item in game_state.stack.items:
        if item.kind != "spell":
            continue
        if item.payload.get("object_id") == target_id or item.payload.get("copy_of") == target_id:
            return True
    return False
