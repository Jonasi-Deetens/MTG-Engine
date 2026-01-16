from __future__ import annotations

from typing import Any, Dict, List, Optional


def extract_enter_choice_requirements(ability_graph: Optional[dict]) -> List[str]:
    if not ability_graph:
        return []
    nodes = ability_graph.get("nodes") or []
    required: List[str] = []
    for node in nodes:
        payload = node.get("data") or {}
        if node.get("type") == "ACTIVATED" and isinstance(payload.get("effect"), dict):
            payload = payload.get("effect") or {}
        if not isinstance(payload, dict):
            continue
        if payload.get("type") != "enter_choice":
            continue
        choice_type = payload.get("choice")
        if not choice_type:
            continue
        if payload.get("choiceValue"):
            continue
        if choice_type not in required:
            required.append(choice_type)
    return required


def validate_enter_choices(ability_graph: Optional[dict], context: Optional[Dict[str, Any]]) -> None:
    required = extract_enter_choice_requirements(ability_graph)
    if not required:
        return
    choices = (context or {}).get("choices") or {}
    enter_choices = choices.get("enter_choices") if isinstance(choices, dict) else None
    if not isinstance(enter_choices, dict):
        raise ValueError("Missing required enter-the-battlefield choices.")
    missing = [choice for choice in required if not enter_choices.get(choice)]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing enter-the-battlefield choices: {missing_text}.")

