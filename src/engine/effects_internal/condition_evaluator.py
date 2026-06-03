"""Condition evaluation for abilities and effects."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from ..state import GameState, ResolveContext

logger = logging.getLogger(__name__)


# Type alias for condition evaluator functions
ConditionHandler = Callable[["GameState", Dict[str, Any], "ResolveContext"], bool]


def _compare(value: int, comparison: str, expected: int) -> bool:
    """Compare two values using the specified comparison operator."""
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


def _previous_result_count(
    previous_results: List[Dict[str, Any]],
    index: int,
) -> Optional[int]:
    if index < 0 or index >= len(previous_results):
        return None
    prev_result = previous_results[index] or {}
    for key in ["found", "cards", "targets", "object_ids", "target_id", "moved"]:
        value = prev_result.get(key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, str):
            return 1
    return 0


class ConditionEvaluator:
    """Evaluates conditions for abilities and effects.

    Responsible for:
    - Evaluating individual conditions
    - Evaluating lists of conditions (AND logic)
    - Registering custom condition handlers
    """

    def __init__(self, game_state: "GameState") -> None:
        self._game_state = game_state
        self._handlers: Dict[str, ConditionHandler] = {}
        self._register_default_handlers()

    def _normalize_condition(self, condition: Any) -> Dict[str, Any]:
        if isinstance(condition, dict):
            return condition
        if hasattr(condition, "model_dump"):
            return condition.model_dump()
        if hasattr(condition, "dict"):
            return condition.dict()
        return {}

    def evaluate(self, condition: Dict[str, Any], context: "ResolveContext") -> bool:
        """Evaluate a single condition."""
        condition = self._normalize_condition(condition)
        condition_type = condition.get("type")

        # Try custom handler first
        handler = self._handlers.get(condition_type)
        if handler:
            return handler(self._game_state, condition, context)

        # Fall back to built-in evaluation
        return self._evaluate_builtin(condition, context)

    def evaluate_all(self, conditions: List[Dict[str, Any]], context: "ResolveContext") -> bool:
        """Evaluate all conditions (AND logic - all must pass)."""
        for condition in conditions:
            if not self.evaluate(condition, context):
                return False
        return True

    def register_handler(self, condition_type: str, handler: ConditionHandler) -> None:
        """Register a custom condition handler."""
        self._handlers[condition_type] = handler

    def _register_default_handlers(self) -> None:
        """Register default condition handlers."""
        # Handlers will be added as needed
        pass

    def _evaluate_builtin(self, condition: Dict[str, Any], context: "ResolveContext") -> bool:
        """Evaluate a built-in condition type."""
        from ..targets import resolve_object, resolve_player_id
        from ..effects_helpers import normalize_card_type

        condition_type = condition.get("type")
        comparison = condition.get("comparison", ">=")
        value = condition.get("value", 0)
        target_key = condition.get("target")
        permanent_type = condition.get("permanentType")
        normalized_type = (
            normalize_card_type(permanent_type)
            if isinstance(permanent_type, str) and permanent_type != "any"
            else permanent_type
        )
        keyword = condition.get("keyword")
        counter_type = condition.get("counterType")

        if condition_type == "control_count":
            player_id = resolve_player_id(context, context.controller_id)
            if player_id is None:
                return False
            count = 0
            for obj_id in self._game_state.get_player(player_id).battlefield:
                obj = self._game_state.objects.get(obj_id)
                if not obj:
                    continue
                if normalized_type and normalized_type != "any" and normalized_type not in obj.types:
                    continue
                count += 1
            return _compare(count, ">=", value)

        if condition_type == "life_total":
            player_id = resolve_player_id(context, context.controller_id)
            if player_id is None:
                return False
            return _compare(self._game_state.get_player(player_id).life, comparison, value)

        if condition_type == "mana_available":
            player_id = resolve_player_id(context, context.controller_id)
            if player_id is None:
                return False
            return _compare(self._game_state.get_player(player_id).total_mana(), comparison, value)

        if condition_type == "battlefield_count":
            player_id = resolve_player_id(context, context.controller_id)
            if player_id is None:
                return False
            count = 0
            for obj_id in self._game_state.get_player(player_id).battlefield:
                obj = self._game_state.objects.get(obj_id)
                if not obj:
                    continue
                if normalized_type and normalized_type != "any" and normalized_type not in obj.types:
                    continue
                count += 1
            return _compare(count, ">=", value)

        if condition_type == "graveyard_count":
            player_id = resolve_player_id(context, context.controller_id)
            if player_id is None:
                return False
            count = 0
            for obj_id in self._game_state.get_player(player_id).graveyard:
                obj = self._game_state.objects.get(obj_id)
                if not obj:
                    continue
                if normalized_type and normalized_type != "any" and normalized_type not in obj.types:
                    continue
                count += 1
            return _compare(count, ">=", value)

        if condition_type == "hand_count":
            player_id = resolve_player_id(context, context.controller_id)
            if player_id is None:
                return False
            count = 0
            for obj_id in self._game_state.get_player(player_id).hand:
                obj = self._game_state.objects.get(obj_id)
                if not obj:
                    continue
                if normalized_type and normalized_type != "any" and normalized_type not in obj.types:
                    continue
                count += 1
            return _compare(count, ">=", value)

        if condition_type == "power_comparison":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            if not obj or obj.power is None:
                return False
            return _compare(obj.power, comparison, value)

        if condition_type == "toughness_comparison":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            if not obj or obj.toughness is None:
                return False
            return _compare(obj.toughness, comparison, value)

        if condition_type == "is_type":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            if not obj:
                return False
            if not normalized_type:
                return False
            return normalized_type in obj.types

        if condition_type == "is_tapped":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            return bool(obj and obj.tapped)

        if condition_type == "is_attacking":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            return bool(obj and obj.is_attacking)

        if condition_type == "is_blocking":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            return bool(obj and obj.is_blocking)

        if condition_type == "has_keyword":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            if not obj or not keyword:
                return False
            return keyword in obj.keywords

        if condition_type == "has_counter":
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            if not obj:
                return False
            counter_value = obj.counters.get(counter_type or "+1/+1", 0)
            return _compare(counter_value, ">=", value)

        if condition_type == "was_cast":
            # Check event payload first (stored in context.targets for triggered abilities)
            if context.targets and context.targets.get("was_cast") is True:
                return True
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            return bool(obj and obj.was_cast)

        if condition_type == "is_cast":
            if context.targets and context.targets.get("was_cast") is True:
                return True
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
            return bool(obj and obj.was_cast)

        if condition_type == "mana_value_comparison":
            source = condition.get("source")
            if source in ("triggering_source", "triggering_aura", "triggering_spell"):
                source_id = {
                    "triggering_source": context.triggering_source_id,
                    "triggering_aura": context.triggering_aura_id,
                    "triggering_spell": context.triggering_spell_id,
                }.get(source)
                source_obj = self._game_state.objects.get(source_id) if source_id else None
                if not source_obj or source_obj.mana_value is None:
                    return False
                return _compare(source_obj.mana_value, comparison, value)
            obj = resolve_object(self._game_state, context, target_key or "target_permanent", context.source_id)
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
            for obj_id in self._game_state.get_player(player_id).graveyard:
                obj = self._game_state.objects.get(obj_id)
                if not obj:
                    continue
                if "creature" not in obj.types:
                    continue
                count += 1
            return _compare(count, comparison, value)

        if condition_type == "previous_effect_result_count":
            index = condition.get("fromEffect", 0)
            if not isinstance(index, int):
                return False
            count = _previous_result_count(context.previous_results, index)
            if count is None:
                return False
            expected = condition.get("value", 1)
            return _compare(count, comparison, expected)

        if condition_type == "previous_effect_has_result":
            index = condition.get("fromEffect", 0)
            if not isinstance(index, int):
                return False
            count = _previous_result_count(context.previous_results, index)
            if count is None:
                return False
            return count > 0

        # Unknown condition type - default to True
        logger.warning(f"Unknown condition type: {condition_type}")
        return True
