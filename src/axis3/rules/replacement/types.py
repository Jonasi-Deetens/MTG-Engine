# axis3/rules/replacement/types.py

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