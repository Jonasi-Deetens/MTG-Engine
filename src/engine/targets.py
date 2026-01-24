from __future__ import annotations

from typing import Any, Dict, Optional, List

from .state import GameState, ResolveContext, GameObject
from .optional_costs import extract_ward_costs_from_graphs
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
    choices = getattr(context, "choices", None)
    if not isinstance(choices, dict):
        return False
    tag = choices.get("alternative_cost_tag", "")
    return isinstance(tag, str) and tag.startswith("overload")


def resolve_object_id(context: ResolveContext, key: str, fallback: Optional[str]) -> Optional[str]:
    if key in context.targets:
        return context.targets[key]
    if key in ("triggering_source", "triggering_aura", "triggering_spell"):
        return {
            "triggering_source": getattr(context, "triggering_source_id", None),
            "triggering_aura": getattr(context, "triggering_aura_id", None) or getattr(context, "triggering_source_id", None),
            "triggering_spell": getattr(context, "triggering_spell_id", None) or getattr(context, "triggering_source_id", None),
        }.get(key)
    if key in ("source", "self"):
        return getattr(context, "source_id", None)
    if key == "target":
        spell_target = context.targets.get("spell_target")
        if spell_target:
            return spell_target
        spell_targets = context.targets.get("spell_targets")
        if isinstance(spell_targets, list) and spell_targets:
            return spell_targets[0]
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


def validate_targets(game_state: GameState, context: ResolveContext, allow_partial: bool = False) -> None:
    if is_overloaded(context):
        return
    if not has_legal_targets(game_state, context, allow_partial=allow_partial):
        issues = get_target_issues(game_state, context)
        if issues:
            raise ValueError("; ".join(issues))
        raise ValueError("No legal targets.")


def _get_target_issues_for_targets(game_state: GameState, context: ResolveContext, targets: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
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
    target_scope = targets.get("target_scope")
    if target_player is not None and not _is_legal_player_target(game_state, context, target_player, target_scope):
        issues.append(f"Player {target_player}: illegal target.")
    if player_list is not None and not any(
        _is_legal_player_target(game_state, context, player_id, target_scope) for player_id in player_list
    ):
        issues.append("No legal player targets.")

    spell_target = targets.get("spell_target")
    spell_list = targets.get("spell_targets") if isinstance(targets.get("spell_targets"), list) else None
    if spell_target is not None and not _is_legal_spell_target(game_state, spell_target):
        issues.append(f"Spell {spell_target}: not on the stack.")
    if spell_list is not None and not any(_is_legal_spell_target(game_state, target_id) for target_id in spell_list):
        issues.append("No legal spell targets.")
    return issues


def get_target_issues(game_state: GameState, context: ResolveContext) -> List[str]:
    if is_overloaded(context):
        return []
    issues: List[str] = []
    for missing in _missing_required_global_targets(context):
        issues.append(f"missing target {missing}")
    distinct_targets_by_effect = getattr(context, "distinct_targets_by_effect", None)
    if isinstance(distinct_targets_by_effect, dict):
        distinct_keys = distinct_targets_by_effect.get("_global", []) or []
        if _has_distinct_violation(context.targets, distinct_keys):
            issues.append("targets must be distinct")
    min_targets_by_effect = getattr(context, "min_targets_by_effect", None)
    if isinstance(min_targets_by_effect, dict):
        min_targets = min_targets_by_effect.get("_global", {}) or {}
        if _has_min_targets_violation(context.targets, min_targets):
            issues.append("not enough targets selected")
    issues.extend(_get_target_issues_for_targets(game_state, context, context.targets))
    targets_by_effect = getattr(context, "targets_by_effect", None)
    required_targets_by_effect = getattr(context, "required_targets_by_effect", None)
    if isinstance(targets_by_effect, dict):
        for node_id, override in targets_by_effect.items():
            if not isinstance(override, dict):
                continue
            merged = dict(context.targets)
            merged.update(override)
            required_keys = []
            if isinstance(required_targets_by_effect, dict):
                required_keys = required_targets_by_effect.get(node_id, []) or []
            for missing in _missing_required_targets(merged, required_keys):
                issues.append(f"{node_id}: missing target {missing}")
            if isinstance(distinct_targets_by_effect, dict):
                distinct_keys = distinct_targets_by_effect.get(node_id, []) or []
                if _has_distinct_violation(merged, distinct_keys):
                    issues.append(f"{node_id}: targets must be distinct")
            if isinstance(min_targets_by_effect, dict):
                min_targets = min_targets_by_effect.get(node_id, {}) or {}
                if _has_min_targets_violation(merged, min_targets):
                    issues.append(f"{node_id}: not enough targets selected")
            for issue in _get_target_issues_for_targets(game_state, context, merged):
                issues.append(f"{node_id}: {issue}")
    # Check required_targets_by_effect for nodes not in targets_by_effect
    if isinstance(required_targets_by_effect, dict):
        checked_nodes = set(targets_by_effect.keys()) if isinstance(targets_by_effect, dict) else set()
        for node_id, required_keys in required_targets_by_effect.items():
            if node_id in checked_nodes or node_id == "_global":
                continue
            if not isinstance(required_keys, list):
                continue
            # For nodes without override, check against base targets
            for missing in _missing_required_targets(context.targets, required_keys):
                issues.append(f"{node_id}: missing target {missing}")
    return issues


def _normalize_targets_for_targets(game_state: GameState, context: ResolveContext, targets: Dict[str, Any]) -> None:
    if "attach_to" in targets and "target" not in targets and "targets" not in targets:
        targets["target"] = targets.get("attach_to")
    if isinstance(targets.get("targets"), list):
        legal = [target_id for target_id in targets["targets"] if _is_legal_object_target(game_state, context, target_id)]
        targets["targets"] = legal
        if "target" not in targets and legal:
            targets["target"] = legal[0]
    if isinstance(targets.get("target_players"), list):
        target_scope = targets.get("target_scope")
        legal_players = [
            player_id
            for player_id in targets["target_players"]
            if _is_legal_player_target(game_state, context, player_id, target_scope)
        ]
        targets["target_players"] = legal_players
        if "target_player" not in targets and legal_players:
            targets["target_player"] = legal_players[0]
    if isinstance(targets.get("spell_targets"), list):
        legal_spells = [target_id for target_id in targets["spell_targets"] if _is_legal_spell_target(game_state, target_id)]
        targets["spell_targets"] = legal_spells
        if "spell_target" not in targets and legal_spells:
            targets["spell_target"] = legal_spells[0]


def normalize_targets(game_state: GameState, context: ResolveContext) -> None:
    if is_overloaded(context):
        return
    _normalize_targets_for_targets(game_state, context, context.targets)
    targets_by_effect = getattr(context, "targets_by_effect", None)
    if isinstance(targets_by_effect, dict):
        for override in targets_by_effect.values():
            if isinstance(override, dict):
                _normalize_targets_for_targets(game_state, context, override)


def _has_legal_targets_for_targets(game_state: GameState, context: ResolveContext, targets: Dict[str, Any]) -> bool:
    target_id = targets.get("target")
    target_list = targets.get("targets") if isinstance(targets.get("targets"), list) else None
    if target_id and not _is_legal_object_target(game_state, context, target_id):
        return False
    if target_list is not None and not any(_is_legal_object_target(game_state, context, target) for target in target_list):
        return False

    target_player = targets.get("target_player")
    player_list = targets.get("target_players") if isinstance(targets.get("target_players"), list) else None
    target_scope = targets.get("target_scope")
    if target_player is not None and not _is_legal_player_target(game_state, context, target_player, target_scope):
        return False
    if player_list is not None and not any(
        _is_legal_player_target(game_state, context, player_id, target_scope) for player_id in player_list
    ):
        return False

    spell_target = targets.get("spell_target")
    spell_list = targets.get("spell_targets") if isinstance(targets.get("spell_targets"), list) else None
    if spell_target is not None and not _is_legal_spell_target(game_state, spell_target):
        return False
    if spell_list is not None and not any(_is_legal_spell_target(game_state, target_id) for target_id in spell_list):
        return False
    return True


def has_legal_targets(game_state: GameState, context: ResolveContext, allow_partial: bool = False) -> bool:
    if is_overloaded(context):
        return True
    if allow_partial:
        required_present = False
        required_targets_by_effect = getattr(context, "required_targets_by_effect", None)
        targets_by_effect = getattr(context, "targets_by_effect", None)
        distinct_targets_by_effect = getattr(context, "distinct_targets_by_effect", None)
        min_targets_by_effect = getattr(context, "min_targets_by_effect", None)
        if isinstance(required_targets_by_effect, dict):
            required_present = any(keys for keys in required_targets_by_effect.values())
        if not required_present and _has_any_target_data(context.targets):
            required_present = True
        if not required_present and isinstance(targets_by_effect, dict):
            for override in targets_by_effect.values():
                if isinstance(override, dict) and _has_any_target_data(override):
                    required_present = True
                    break
        if not required_present:
            return True
        bucket: set[tuple[str, Any]] = set()
        _collect_legal_targets(game_state, context, context.targets, bucket)
        if isinstance(targets_by_effect, dict):
            for override in targets_by_effect.values():
                if not isinstance(override, dict):
                    continue
                merged = dict(context.targets)
                merged.update(override)
                _collect_legal_targets(game_state, context, merged, bucket)
        return len(bucket) > 0
    if _missing_required_global_targets(context):
        return False
    distinct_targets_by_effect = getattr(context, "distinct_targets_by_effect", None)
    min_targets_by_effect = getattr(context, "min_targets_by_effect", None)
    targets_by_effect = getattr(context, "targets_by_effect", None)
    required_targets_by_effect = getattr(context, "required_targets_by_effect", None)
    if isinstance(distinct_targets_by_effect, dict):
        distinct_keys = distinct_targets_by_effect.get("_global", []) or []
        if _has_distinct_violation(context.targets, distinct_keys):
            return False
    if isinstance(min_targets_by_effect, dict):
        min_targets = min_targets_by_effect.get("_global", {}) or {}
        if _has_min_targets_violation(context.targets, min_targets):
            return False
    if not _has_legal_targets_for_targets(game_state, context, context.targets):
        return False
    if isinstance(targets_by_effect, dict):
        for node_id, override in targets_by_effect.items():
            if not isinstance(override, dict):
                continue
            merged = dict(context.targets)
            merged.update(override)
            required_keys = []
            if isinstance(required_targets_by_effect, dict):
                required_keys = required_targets_by_effect.get(node_id, []) or []
            if _missing_required_targets(merged, required_keys):
                return False
            if isinstance(distinct_targets_by_effect, dict):
                distinct_keys = distinct_targets_by_effect.get(node_id, []) or []
                if _has_distinct_violation(merged, distinct_keys):
                    return False
            if isinstance(min_targets_by_effect, dict):
                min_targets = min_targets_by_effect.get(node_id, {}) or {}
                if _has_min_targets_violation(merged, min_targets):
                    return False
            if not _has_legal_targets_for_targets(game_state, context, merged):
                return False
    # Check required_targets_by_effect for nodes not in targets_by_effect
    if isinstance(required_targets_by_effect, dict):
        checked_nodes = set(targets_by_effect.keys()) if isinstance(targets_by_effect, dict) else set()
        for node_id, required_keys in required_targets_by_effect.items():
            if node_id in checked_nodes or node_id == "_global":
                continue
            if not isinstance(required_keys, list):
                continue
            # For nodes without override, check against base targets
            if _missing_required_targets(context.targets, required_keys):
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
    scope = context.targets.get("target_object_scope")
    if scope == "you_control" and context.controller_id is not None:
        if obj.controller_id != context.controller_id:
            return False, "Target is not controlled by you."
    if scope == "opponent_control" and context.controller_id is not None:
        if obj.controller_id == context.controller_id:
            return False, "Target is not controlled by an opponent."
    type_filter = context.targets.get("target_object_types")
    if isinstance(type_filter, list) and type_filter:
        if not any(type_name in (obj.types or []) for type_name in type_filter):
            return False, "Target does not match required types."
    if "Shroud" in obj.keywords:
        return False, "Target has shroud."
    if "Hexproof" in obj.keywords and context.controller_id is not None:
        if obj.controller_id != context.controller_id:
            return False, "Target has hexproof."
    source_id = (
        getattr(context, "source_id", None)
        or getattr(context, "triggering_source_id", None)
        or getattr(context, "triggering_spell_id", None)
        or getattr(context, "triggering_aura_id", None)
    )
    if obj.protections and source_id:
        source = game_state.objects.get(source_id)
        if source and any(color in obj.protections for color in source.colors):
            return False, "Target has protection from source."
    return True, None


def _collect_target_ids(context: ResolveContext) -> List[str]:
    targets = []

    def add_target(value: Any) -> None:
        if isinstance(value, str) and value not in targets:
            targets.append(value)

    def add_targets_from_dict(payload: Dict[str, Any]) -> None:
        add_target(payload.get("target"))
        add_target(payload.get("yourCreature"))
        add_target(payload.get("opponentCreature"))
        add_target(payload.get("sourceTarget"))
        add_target(payload.get("redirectTarget"))
        add_target(payload.get("attach_to"))
        extra = payload.get("targets")
        if isinstance(extra, list):
            for obj_id in extra:
                add_target(obj_id)

    add_targets_from_dict(context.targets or {})
    if isinstance(context.targets_by_effect, dict):
        for entry in context.targets_by_effect.values():
            if isinstance(entry, dict):
                add_targets_from_dict(entry)
    return targets


def _has_any_target_data(targets: Dict[str, Any]) -> bool:
    if targets.get("target"):
        return True
    if targets.get("targets"):
        return True
    if targets.get("target_player") is not None:
        return True
    if targets.get("target_players"):
        return True
    if targets.get("spell_target"):
        return True
    if targets.get("spell_targets"):
        return True
    if targets.get("yourCreature"):
        return True
    if targets.get("opponentCreature"):
        return True
    if targets.get("sourceTarget"):
        return True
    if targets.get("redirectTarget"):
        return True
    if targets.get("attach_to"):
        return True
    return False


def _missing_required_targets(targets: Dict[str, Any], required_keys: List[str]) -> List[str]:
    missing = []
    for key in required_keys:
        if key == "target":
            if (
                not targets.get("target")
                and not targets.get("targets")
                and not targets.get("target_player")
                and not targets.get("target_players")
                and not targets.get("spell_target")
                and not targets.get("spell_targets")
            ):
                missing.append(key)
        elif key == "redirectTarget":
            if not targets.get("redirectTarget") and not targets.get("target_player") and not targets.get("target_players"):
                missing.append(key)
        else:
            if not targets.get(key):
                missing.append(key)
    return missing


def _missing_required_global_targets(context: ResolveContext) -> List[str]:
    required_targets_by_effect = getattr(context, "required_targets_by_effect", None)
    if not isinstance(required_targets_by_effect, dict):
        return []
    required = required_targets_by_effect.get("_global", []) or []
    return _missing_required_targets(context.targets, required)


def has_missing_required_targets(context: ResolveContext) -> bool:
    if _missing_required_global_targets(context):
        return True
    targets_by_effect = getattr(context, "targets_by_effect", None)
    required_targets_by_effect = getattr(context, "required_targets_by_effect", None)
    if isinstance(targets_by_effect, dict):
        for node_id, override in targets_by_effect.items():
            if not isinstance(override, dict):
                continue
            required_keys: List[str] = []
            if isinstance(required_targets_by_effect, dict):
                required_keys = required_targets_by_effect.get(node_id, []) or []
            if not required_keys:
                continue
            merged = dict(context.targets)
            merged.update(override)
            if _missing_required_targets(merged, required_keys):
                return True
    return False


def _collect_target_units(targets: Dict[str, Any]) -> tuple[List[str], List[int]]:
    object_ids: List[str] = []
    player_ids: List[int] = []
    target_id = targets.get("target")
    if isinstance(target_id, str):
        object_ids.append(target_id)
    target_list = targets.get("targets") if isinstance(targets.get("targets"), list) else None
    if target_list:
        object_ids.extend([target for target in target_list if isinstance(target, str)])
    spell_target = targets.get("spell_target")
    if isinstance(spell_target, str):
        object_ids.append(spell_target)
    spell_list = targets.get("spell_targets") if isinstance(targets.get("spell_targets"), list) else None
    if spell_list:
        object_ids.extend([target for target in spell_list if isinstance(target, str)])
    target_player = targets.get("target_player")
    if isinstance(target_player, int):
        player_ids.append(target_player)
    player_list = targets.get("target_players") if isinstance(targets.get("target_players"), list) else None
    if player_list:
        player_ids.extend([player_id for player_id in player_list if isinstance(player_id, int)])
    return object_ids, player_ids


def _has_distinct_violation(targets: Dict[str, Any], distinct_keys: List[str]) -> bool:
    if not distinct_keys:
        return False
    object_ids, player_ids = _collect_target_units(targets)
    if "target" in distinct_keys:
        if object_ids and len(set(object_ids)) != len(object_ids):
            return True
        if player_ids and len(set(player_ids)) != len(player_ids):
            return True
    key_map = {
        "yourCreature": "object",
        "opponentCreature": "object",
        "sourceTarget": "object",
        "redirectTarget": "object_or_player",
        "attach_to": "object",
    }
    selected_objects: List[str] = []
    selected_players: List[int] = []
    for key in distinct_keys:
        if key == "target":
            continue
        kind = key_map.get(key)
        if kind is None:
            continue
        if key == "redirectTarget":
            redirect = targets.get("redirectTarget")
            if isinstance(redirect, str):
                selected_objects.append(redirect)
            target_player = targets.get("target_player")
            if isinstance(target_player, int):
                selected_players.append(target_player)
            target_players = targets.get("target_players") if isinstance(targets.get("target_players"), list) else None
            if target_players:
                selected_players.extend([player_id for player_id in target_players if isinstance(player_id, int)])
            continue
        value = targets.get(key)
        if kind == "object" and isinstance(value, str):
            selected_objects.append(value)
        if kind == "player" and isinstance(value, int):
            selected_players.append(value)
    if selected_objects and len(set(selected_objects)) != len(selected_objects):
        return True
    if selected_players and len(set(selected_players)) != len(selected_players):
        return True
    return False


def _has_min_targets_violation(targets: Dict[str, Any], min_targets: Dict[str, int]) -> bool:
    if not min_targets:
        return False
    min_target = min_targets.get("target")
    if isinstance(min_target, int) and min_target > 0:
        object_ids, player_ids = _collect_target_units(targets)
        count = len(set(object_ids)) + len(set(player_ids))
        return count < min_target
    return False


def _collect_legal_targets(
    game_state: GameState,
    context: ResolveContext,
    targets: Dict[str, Any],
    bucket: set[tuple[str, Any]],
) -> None:
    target_id = targets.get("target")
    if target_id and _is_legal_object_target(game_state, context, target_id):
        bucket.add(("object", target_id))
    target_list = targets.get("targets") if isinstance(targets.get("targets"), list) else None
    if target_list is not None:
        for target in target_list:
            if _is_legal_object_target(game_state, context, target):
                bucket.add(("object", target))
    target_player = targets.get("target_player")
    target_scope = targets.get("target_scope")
    if target_player is not None and _is_legal_player_target(game_state, context, target_player, target_scope):
        bucket.add(("player", target_player))
    player_list = targets.get("target_players") if isinstance(targets.get("target_players"), list) else None
    if player_list is not None:
        for player_id in player_list:
            if _is_legal_player_target(game_state, context, player_id, target_scope):
                bucket.add(("player", player_id))
    spell_target = targets.get("spell_target")
    if spell_target is not None and _is_legal_spell_target(game_state, spell_target):
        bucket.add(("spell", spell_target))
    spell_list = targets.get("spell_targets") if isinstance(targets.get("spell_targets"), list) else None
    if spell_list is not None:
        for target_id in spell_list:
            if _is_legal_spell_target(game_state, target_id):
                bucket.add(("spell", target_id))


def _ward_cost_entries(obj: GameObject) -> List[Dict[str, Any]]:
    return extract_ward_costs_from_graphs(obj.effect_graphs or [])


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


def is_legal_object_target(game_state: GameState, context: ResolveContext, target_id: str) -> bool:
    return _is_legal_object_target(game_state, context, target_id)


def _is_legal_player_target(
    game_state: GameState,
    context: ResolveContext,
    player_id: int,
    target_scope: str | None = None,
) -> bool:
    controller_id = context.controller_id
    for player in game_state.players:
        if player.id != player_id or getattr(player, "removed_from_game", False):
            continue
        if target_scope == "opponent" and controller_id is not None and player.id == controller_id:
            return False
        if target_scope == "controller" and controller_id is not None and player.id != controller_id:
            return False
        return True
    return False


def _is_legal_spell_target(game_state: GameState, target_id: str) -> bool:
    for item in game_state.stack.items:
        if item.kind != "spell":
            continue
        if item.payload.get("object_id") == target_id or item.payload.get("copy_of") == target_id:
            return True
    return False
