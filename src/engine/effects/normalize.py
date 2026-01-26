from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from api.schemas.unified_effect_schemas import EffectGraph, UnifiedEffect


def normalize_effect(effect: Any) -> UnifiedEffect:
    if isinstance(effect, UnifiedEffect):
        return effect

    if not isinstance(effect, dict):
        raise ValueError("effect must be a dict or UnifiedEffect instance")

    data = deepcopy(effect)

    data.setdefault("resolution", "stack")
    data.setdefault("persistence", "instant")
    data.setdefault("tags", [])
    data.setdefault("conditions", [])

    body = data.get("effect") or {}
    if isinstance(body, dict) and body.get("kind") == "continuous":
        data["persistence"] = "continuous"

    return UnifiedEffect(**data)


def _apply_linked_condition_indices(effect_data: Dict[str, Any], id_to_index: Dict[str, int]) -> Dict[str, Any]:
    conditions = effect_data.get("conditions")
    if not isinstance(conditions, list):
        return effect_data
    updated = []
    for condition in conditions:
        if not isinstance(condition, dict):
            updated.append(condition)
            continue
        condition_type = condition.get("type")
        if condition_type not in ("previous_effect_has_result", "previous_effect_result_count"):
            updated.append(condition)
            continue
        linked_to = condition.get("linkedToStepId")
        if linked_to and linked_to in id_to_index:
            condition = dict(condition)
            condition["fromEffect"] = id_to_index[linked_to]
        updated.append(condition)
    effect_data["conditions"] = updated
    return effect_data


def normalize_graph(graph: Any) -> EffectGraph:
    if isinstance(graph, EffectGraph):
        return graph

    if not isinstance(graph, dict):
        raise ValueError("graph must be a dict or EffectGraph instance")

    data: Dict[str, Any] = deepcopy(graph)
    data.setdefault("sourceKind", "permanent")

    steps = data.get("steps")
    if not isinstance(steps, list):
        raise ValueError("graph must include a list of steps")

    id_to_index: Dict[str, int] = {}
    for index, step in enumerate(steps):
        if isinstance(step, dict) and "id" in step:
            id_to_index[step["id"]] = index

    normalized_steps = []
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError("step entries must be objects")
        if "id" not in step:
            raise ValueError("each step must include an id")
        if "effect" not in step:
            raise ValueError("each step must include an effect")

        step_copy = dict(step)
        effect_value = step_copy["effect"]
        if isinstance(effect_value, UnifiedEffect):
            effect_dict = effect_value.model_dump(by_alias=True)
            effect_dict = _apply_linked_condition_indices(effect_dict, id_to_index)
            step_copy["effect"] = normalize_effect(effect_dict)
        elif isinstance(effect_value, dict):
            effect_dict = _apply_linked_condition_indices(dict(effect_value), id_to_index)
            step_copy["effect"] = normalize_effect(effect_dict)
        else:
            step_copy["effect"] = normalize_effect(effect_value)
        normalized_steps.append(step_copy)

    data["steps"] = normalized_steps

    return EffectGraph(**data)
