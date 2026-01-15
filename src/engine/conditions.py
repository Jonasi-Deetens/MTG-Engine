from __future__ import annotations

from typing import Any, Dict, Optional

from .state import GameState, ResolveContext
from .targets import resolve_object, resolve_player_id


def _compare(value: int, comparison: str, expected: int) -> bool:
    if comparison == ">":
        return value > expected
    if comparison == ">=":
        return value >= expected
    if comparison == "<":
        return value < expected
    if comparison == "<=":
        return value <= expected
    if comparison == "==":
        return value == expected
    if comparison == "!=":
        return value != expected
    return False


def evaluate_condition(game_state: GameState, condition: Dict[str, Any], context: ResolveContext) -> bool:
    condition_type = condition.get("type")
    comparison = condition.get("comparison", ">=")
    value = condition.get("value", 0)
    target_key = condition.get("target")
    permanent_type = condition.get("permanentType")
    keyword = condition.get("keyword")
    counter_type = condition.get("counterType")

    if condition_type == "control_count":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        count = 0
        for obj_id in game_state.get_player(player_id).battlefield:
            obj = game_state.objects.get(obj_id)
            if not obj:
                continue
            if permanent_type and permanent_type != "any" and permanent_type not in obj.types:
                continue
            count += 1
        return _compare(count, ">=", value)

    if condition_type == "life_total":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        return _compare(game_state.get_player(player_id).life, comparison, value)

    if condition_type == "mana_available":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        return _compare(game_state.get_player(player_id).total_mana(), comparison, value)

    if condition_type == "battlefield_count":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        count = 0
        for obj_id in game_state.get_player(player_id).battlefield:
            obj = game_state.objects.get(obj_id)
            if not obj:
                continue
            if permanent_type and permanent_type != "any" and permanent_type not in obj.types:
                continue
            count += 1
        return _compare(count, ">=", value)

    if condition_type == "graveyard_count":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        count = len(game_state.get_player(player_id).graveyard)
        return _compare(count, ">=", value)

    if condition_type == "hand_count":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        count = len(game_state.get_player(player_id).hand)
        return _compare(count, ">=", value)

    if condition_type == "power_comparison":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        if not obj or obj.power is None:
            return False
        return _compare(obj.power, comparison, value)

    if condition_type == "toughness_comparison":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        if not obj or obj.toughness is None:
            return False
        return _compare(obj.toughness, comparison, value)

    if condition_type == "is_type":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        if not obj:
            return False
        if not permanent_type:
            return False
        return permanent_type in obj.types

    if condition_type == "is_tapped":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        return bool(obj and obj.tapped)

    if condition_type == "is_attacking":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        return bool(obj and obj.is_attacking)

    if condition_type == "is_blocking":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        return bool(obj and obj.is_blocking)

    if condition_type == "has_keyword":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        if not obj or not keyword:
            return False
        return keyword in obj.keywords

    if condition_type == "has_counter":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        if not obj:
            return False
        counter_value = obj.counters.get(counter_type or "+1/+1", 0)
        return _compare(counter_value, ">=", value)

    if condition_type == "was_cast":
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        return bool(obj and obj.was_cast)

    if condition_type == "mana_value_comparison":
        source = condition.get("source")
        if source in ("triggering_source", "triggering_aura", "triggering_spell"):
            source_id = {
                "triggering_source": context.triggering_source_id,
                "triggering_aura": context.triggering_aura_id,
                "triggering_spell": context.triggering_spell_id,
            }.get(source)
            source_obj = game_state.objects.get(source_id) if source_id else None
            if not source_obj or source_obj.mana_value is None:
                return False
            return _compare(source_obj.mana_value, comparison, value)
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        if not obj or obj.mana_value is None:
            return False
        return _compare(obj.mana_value, comparison, value)

    return True


def evaluate_conditions(game_state: GameState, conditions: list[Dict[str, Any]], context: ResolveContext) -> bool:
    for condition in conditions:
        if not evaluate_condition(game_state, condition, context):
            return False
    return True
