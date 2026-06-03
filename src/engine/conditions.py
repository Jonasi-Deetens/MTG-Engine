from __future__ import annotations

from typing import Any, Dict, List, Optional

from .state import GameState, ResolveContext
from .targets import resolve_object, resolve_player_id

# Import from new module
from .effects_internal.condition_evaluator import ConditionEvaluator, _compare


def evaluate_condition(game_state: GameState, condition: Dict[str, Any], context: ResolveContext) -> bool:
    """Evaluate a single condition.

    This function maintains backward compatibility while using ConditionEvaluator internally.
    """
    evaluator = ConditionEvaluator(game_state)
    return evaluator.evaluate(condition, context)


def _evaluate_condition_legacy(game_state: GameState, condition: Dict[str, Any], context: ResolveContext) -> bool:
    """Legacy condition evaluation (kept for reference)."""
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
        count = 0
        for obj_id in game_state.get_player(player_id).graveyard:
            obj = game_state.objects.get(obj_id)
            if not obj:
                continue
            if permanent_type and permanent_type != "any" and permanent_type not in obj.types:
                continue
            count += 1
        return _compare(count, ">=", value)

    if condition_type == "hand_count":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        count = 0
        for obj_id in game_state.get_player(player_id).hand:
            obj = game_state.objects.get(obj_id)
            if not obj:
                continue
            if permanent_type and permanent_type != "any" and permanent_type not in obj.types:
                continue
            count += 1
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
        # Check event payload first (stored in context.targets for triggered abilities)
        if context.targets and context.targets.get("was_cast") is True:
            return True
        obj = resolve_object(game_state, context, target_key or "target_permanent", context.source_id)
        return bool(obj and obj.was_cast)

    if condition_type == "is_cast":
        if context.targets and context.targets.get("was_cast") is True:
            return True
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

    if condition_type == "kicked":
        choices = context.choices if isinstance(context.choices, dict) else {}
        return bool(choices.get("kicked"))

    if condition_type == "kicker_count":
        choices = context.choices if isinstance(context.choices, dict) else {}
        count = int(choices.get("kicker_count") or 0)
        return _compare(count, comparison, value)

    if condition_type == "creatures_in_graveyard":
        player_id = resolve_player_id(context, context.controller_id)
        if player_id is None:
            return False
        count = 0
        for obj_id in game_state.get_player(player_id).graveyard:
            obj = game_state.objects.get(obj_id)
            if not obj:
                continue
            if "creature" not in obj.types:
                continue
            count += 1
        return _compare(count, comparison, value)

    return True


def evaluate_conditions(game_state: GameState, conditions: List[Dict[str, Any]], context: ResolveContext) -> bool:
    """Evaluate all conditions (AND logic - all must pass).

    This function maintains backward compatibility while using ConditionEvaluator internally.
    """
    evaluator = ConditionEvaluator(game_state)
    return evaluator.evaluate_all(conditions, context)
