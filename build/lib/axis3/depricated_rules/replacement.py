# src/axis3/rules/replacement.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional


@dataclass
class ReplacementEffect:
    """
    A runtime replacement effect derived from Axis2.
    """
    source_id: Optional[int]  # None for global effects
    applies_to: str           # e.g. "zone_change", "draw", "damage"
    condition: Callable[[Dict[str, Any]], bool]
    apply: Callable[[Dict[str, Any]], Dict[str, Any]]

def apply_replacement_effects(game_state, event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all replacement effects that match this event.
    Replacement effects may modify the event or replace it entirely.
    """

    changed = True
    while changed:
        changed = False

        for effect in list(game_state.replacement_effects):
            if effect.applies_to != event["type"]:
                continue

            if effect.condition(event):
                event = effect.apply(event)
                changed = True

    return event
