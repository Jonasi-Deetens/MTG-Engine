from __future__ import annotations

from typing import Any, Dict, List
import copy

from .effects_helpers import resolve_target_object
from .stack import StackItem
from .targets import resolve_object_id
from .targets import normalize_targets, validate_targets
from .state import ResolveContext


def handle_copy_spell(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target_spell = resolve_object_id(context, "target", None)
    if not target_spell:
        return {"type": "copy_spell", "status": "no_target"}
    target_item = None
    for item in resolver.game_state.stack.items:
        if item.kind not in ("spell", "effect_graph"):
            continue
        if (
            item.payload.get("object_id") == target_spell
            or item.payload.get("copy_of") == target_spell
            or item.payload.get("source_object_id") == target_spell
        ):
            target_item = item
            break
    if not target_item:
        return {"type": "copy_spell", "status": "no_target"}
    choose_new_targets = bool(effect.get("chooseNewTargets")) or bool(
        context.choices.get("copy_choose_new_targets")
    )
    copies = int(effect.get("amount", 1) or 1)
    if copies < 1:
        return {"type": "copy_spell", "status": "no_copies"}

    def _copy_target_overrides(index: int) -> Dict[str, Any]:
        overrides: Dict[str, Any] = {}
        if not choose_new_targets:
            return overrides
        target_list = context.choices.get("copy_targets_list")
        targets_by_effect_list = context.choices.get("copy_targets_by_effect_list")
        if isinstance(target_list, list) and index < len(target_list):
            if isinstance(target_list[index], dict):
                overrides["targets"] = target_list[index]
        elif isinstance(context.choices.get("copy_targets"), dict):
            overrides["targets"] = context.choices.get("copy_targets")
        if isinstance(targets_by_effect_list, list) and index < len(targets_by_effect_list):
            if isinstance(targets_by_effect_list[index], dict):
                overrides["targets_by_effect"] = targets_by_effect_list[index]
        elif isinstance(context.choices.get("copy_targets_by_effect"), dict):
            overrides["targets_by_effect"] = context.choices.get("copy_targets_by_effect")
        if isinstance(context.choices.get("copy_required_targets_by_effect_list"), list):
            entries = context.choices.get("copy_required_targets_by_effect_list")
            if index < len(entries) and isinstance(entries[index], dict):
                overrides["required_targets_by_effect"] = entries[index]
        elif isinstance(context.choices.get("copy_required_targets_by_effect"), dict):
            overrides["required_targets_by_effect"] = context.choices.get("copy_required_targets_by_effect")
        if isinstance(context.choices.get("copy_distinct_targets_by_effect_list"), list):
            entries = context.choices.get("copy_distinct_targets_by_effect_list")
            if index < len(entries) and isinstance(entries[index], dict):
                overrides["distinct_targets_by_effect"] = entries[index]
        elif isinstance(context.choices.get("copy_distinct_targets_by_effect"), dict):
            overrides["distinct_targets_by_effect"] = context.choices.get("copy_distinct_targets_by_effect")
        if isinstance(context.choices.get("copy_min_targets_by_effect_list"), list):
            entries = context.choices.get("copy_min_targets_by_effect_list")
            if index < len(entries) and isinstance(entries[index], dict):
                overrides["min_targets_by_effect"] = entries[index]
        elif isinstance(context.choices.get("copy_min_targets_by_effect"), dict):
            overrides["min_targets_by_effect"] = context.choices.get("copy_min_targets_by_effect")
        return overrides

    def _apply_overrides_to_context(context_data: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        if "targets" in overrides:
            context_data["targets"] = overrides.get("targets")
        if "targets_by_effect" in overrides:
            context_data["targets_by_effect"] = overrides.get("targets_by_effect")
        if "required_targets_by_effect" in overrides:
            context_data["required_targets_by_effect"] = overrides.get("required_targets_by_effect")
        if "distinct_targets_by_effect" in overrides:
            context_data["distinct_targets_by_effect"] = overrides.get("distinct_targets_by_effect")
        if "min_targets_by_effect" in overrides:
            context_data["min_targets_by_effect"] = overrides.get("min_targets_by_effect")
        return context_data

    def _validate_copy_targets(context_data: Dict[str, Any]) -> None:
        ctx = ResolveContext(**context_data)
        normalize_targets(resolver.game_state, ctx)
        validate_targets(resolver.game_state, ctx)
    for index in range(copies):
        overrides = _copy_target_overrides(index)
        if target_item.kind == "effect_graph":
            payload = copy.deepcopy(target_item.payload or {})
            context_data = copy.deepcopy(payload.get("context") or {})
            if context_data.get("source_id") is None:
                context_data["source_id"] = payload.get("source_object_id") or target_spell
            if context_data.get("controller_id") is None and context.controller_id is not None:
                context_data["controller_id"] = context.controller_id
            if overrides:
                context_data = _apply_overrides_to_context(context_data, overrides)
                _validate_copy_targets(context_data)
            payload["context"] = context_data
            payload["copy_of"] = target_spell
            payload["is_copy"] = True
            payload["source_object_id"] = None
            payload["destination_zone"] = None
            resolver.game_state.stack.push(
                StackItem(kind="effect_graph", payload=payload, controller_id=context.controller_id)
            )
        else:
            payload = copy.deepcopy(target_item.payload or {})
            if overrides:
                payload_context = copy.deepcopy(payload.get("context") or {})
                payload_context = _apply_overrides_to_context(payload_context, overrides)
                _validate_copy_targets(payload_context)
                payload["context"] = payload_context
            payload["copy_of"] = target_spell
            payload["is_copy"] = True
            payload.pop("object_id", None)
            payload.pop("destination_zone", None)
            resolver.game_state.stack.push(
                StackItem(kind="spell", payload=payload, controller_id=context.controller_id)
            )
    return {"type": "copy_spell", "copy_of": target_spell, "copies": copies}


def handle_copy_permanent(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    source_id = context.source_id
    if not target or not source_id:
        return {"type": "copy_permanent", "status": "no_target"}
    source = resolver.game_state.objects.get(source_id)
    if not source:
        return {"type": "copy_permanent", "status": "no_source"}
    resolver._add_temporary_effect(source, {
        "type": "copy_object",
        "source_id": target.id,
        "duration": effect.get("duration"),
    })
    return {"type": "copy_permanent", "source_id": source.id, "target_id": target.id}


def handle_enter_copy(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not target:
        return {"type": "enter_copy", "status": "no_target"}
    context.choices["enter_copy_of"] = target.id
    return {"type": "enter_copy", "target_id": target.id}


def handle_enter_choice(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    choice_type = effect.get("choice")
    if not choice_type:
        return {"type": "enter_choice", "status": "no_choice"}
    choice_value = effect.get("choiceValue")
    enter_choices = context.choices.get("enter_choices")
    if not isinstance(enter_choices, dict):
        enter_choices = {}
        context.choices["enter_choices"] = enter_choices
    enter_choices[choice_type] = choice_value
    return {"type": "enter_choice", "choice": choice_type, "value": choice_value}


__all__ = [
    "handle_copy_spell",
    "handle_copy_permanent",
    "handle_enter_copy",
    "handle_enter_choice",
]

