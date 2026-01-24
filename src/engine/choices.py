from __future__ import annotations

from typing import Any, Dict, List, Optional




def extract_enter_choice_requirements_effect_graph(effect_graph: Optional[dict]) -> List[str]:
    if not effect_graph or not isinstance(effect_graph, dict):
        return []
    steps = effect_graph.get("steps") or []
    required: List[str] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        effect = step.get("effect") or {}
        body = effect.get("effect") or {}
        if not isinstance(body, dict):
            continue
        if body.get("kind") != "one_shot":
            continue
        action = body.get("action") or {}
        if not isinstance(action, dict):
            continue
        if action.get("type") != "enter_choice":
            continue
        choice_type = action.get("choice")
        if not choice_type:
            continue
        if action.get("choiceValue"):
            continue
        if choice_type not in required:
            required.append(choice_type)
    return required


def validate_enter_choices_effect_graph(effect_graph: Optional[dict], context: Optional[Dict[str, Any]]) -> None:
    required = extract_enter_choice_requirements_effect_graph(effect_graph)
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




def _normalize_chosen_modes(choices: Any) -> List[str]:
    if not isinstance(choices, dict):
        return []
    raw = choices.get("chosen_modes")
    if raw is None:
        raw = choices.get("chosen_mode")
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        values = [entry for entry in raw if isinstance(entry, str) and entry]
        return values
    return []



def validate_modal_choices_effect_graph(effect_graph: Optional[dict], context: Optional[Dict[str, Any]]) -> None:
    if not effect_graph or not isinstance(effect_graph, dict):
        return
    modal = effect_graph.get("modal")
    if not isinstance(modal, dict):
        return
    choices = (context or {}).get("choices") if isinstance(context, dict) else None
    selected = _normalize_chosen_modes(choices)
    entwine = bool(choices.get("entwine")) if isinstance(choices, dict) else False
    min_required = modal.get("min") if isinstance(modal, dict) else None
    max_allowed = modal.get("max") if isinstance(modal, dict) else None
    min_required = int(min_required) if isinstance(min_required, int) and min_required >= 0 else 1
    max_allowed = int(max_allowed) if isinstance(max_allowed, int) and max_allowed > 0 else None
    if not selected:
        if entwine:
            return
        if min_required == 0:
            return
        raise ValueError("Missing modal choices.")
    if len(set(selected)) != len(selected):
        raise ValueError("Duplicate modal choices.")
    modes = modal.get("modes") if isinstance(modal, dict) else None
    if not isinstance(modes, list) or not modes:
        return
    allowed = [entry.get("id") for entry in modes if isinstance(entry, dict) and entry.get("id")]
    allowed_set = set([entry for entry in allowed if isinstance(entry, str)])
    invalid = [mode for mode in selected if mode not in allowed_set]
    if invalid:
        raise ValueError(f"Invalid modal choice(s): {', '.join(invalid)}.")
    if entwine:
        if len(selected) != len(allowed_set):
            raise ValueError("Entwine requires choosing all modes.")
        return
    if len(selected) < min_required:
        raise ValueError(f"Select at least {min_required} mode(s).")
    if max_allowed is not None and len(selected) > max_allowed:
        raise ValueError(f"Select no more than {max_allowed} mode(s).")