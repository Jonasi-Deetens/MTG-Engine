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


def _extract_modal_config_from_graph(ability_graph: Optional[dict]) -> Optional[Dict[str, Any]]:
    if not ability_graph:
        return None
    modal = ability_graph.get("modal")
    if isinstance(modal, dict):
        return modal
    root_id = ability_graph.get("rootNodeId")
    nodes = ability_graph.get("nodes") or []
    if root_id and isinstance(nodes, list):
        for node in nodes:
            if node.get("id") == root_id:
                data = node.get("data") or {}
                if isinstance(data, dict) and isinstance(data.get("modal"), dict):
                    return data.get("modal")
    return None


def _infer_modal_config_from_effects(ability_graph: Optional[dict]) -> Optional[Dict[str, Any]]:
    if not ability_graph:
        return None
    nodes = ability_graph.get("nodes") or []
    if not isinstance(nodes, list):
        return None
    modes: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for node in nodes:
        if node.get("type") != "EFFECT":
            continue
        data = node.get("data") or {}
        if not isinstance(data, dict):
            continue
        mode_id = data.get("modeId")
        if not mode_id or not isinstance(mode_id, str):
            continue
        if mode_id in seen:
            continue
        seen.add(mode_id)
        label = data.get("modeLabel") if isinstance(data.get("modeLabel"), str) else mode_id
        modes.append({"id": mode_id, "label": label})
    if not modes:
        return None
    return {"min": 1, "max": 1, "modes": modes}


def extract_modal_config(ability_graph: Optional[dict]) -> Optional[Dict[str, Any]]:
    modal = _extract_modal_config_from_graph(ability_graph)
    if modal:
        return modal
    return _infer_modal_config_from_effects(ability_graph)


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


def validate_modal_choices(ability_graph: Optional[dict], context: Optional[Dict[str, Any]]) -> None:
    modal = extract_modal_config(ability_graph)
    if not modal:
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