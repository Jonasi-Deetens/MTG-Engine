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

    normalized_steps = []
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError("step entries must be objects")
        if "id" not in step:
            raise ValueError("each step must include an id")
        if "effect" not in step:
            raise ValueError("each step must include an effect")

        step_copy = dict(step)
        step_copy["effect"] = normalize_effect(step_copy["effect"])
        normalized_steps.append(step_copy)

    data["steps"] = normalized_steps

    return EffectGraph(**data)
