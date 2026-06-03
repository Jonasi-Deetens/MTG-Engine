# axis2/parsing/effects/fallback.py
"""Guaranteed fallback parser — ensures every clause becomes an Effect object."""

from __future__ import annotations

import re
from typing import List

from .base import EffectParser, ParseResult
from axis2.schema import ParseContext, UnparsedOracleEffect

_HINT_KEYWORDS = [
    "damage", "draw", "destroy", "exile", "create", "token", "counter",
    "search", "return", "gain", "lose", "life", "tap", "untap", "sacrifice",
    "fight", "mill", "scry", "surveil", "copy", "counter", "transform",
    "proliferate", "venture", "dungeon", "choose", "target", "opponent",
    "library", "graveyard", "battlefield", "attach", "equip",
]


def _detect_hints(text: str) -> List[str]:
    t = text.lower()
    return [kw for kw in _HINT_KEYWORDS if kw in t]


def _detect_kind(text: str) -> str | None:
    t = text.lower()
    if "create" in t and "token" in t:
        return "token"
    if "damage" in t and "deal" in t:
        return "damage"
    if "draw" in t:
        return "draw"
    if "destroy" in t:
        return "destroy"
    if "exile" in t:
        return "exile"
    if "search" in t and "library" in t:
        return "search"
    if "lose" in t and "life" in t:
        return "lose_life"
    if "gain" in t and "life" in t:
        return "gain_life"
    if "mill" in t:
        return "mill"
    if "fight" in t or "battles" in t:
        return "fight"
    if "proliferate" in t:
        return "proliferate"
    if "venture" in t or "dungeon" in t:
        return "venture"
    if "copy" in t:
        return "copy"
    return None


class FallbackParser(EffectParser):
    """
    Lowest priority: always produces UnparsedOracleEffect.
    Registered last so specialized parsers win when they match.
    """

    priority = 0

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return bool(text and text.strip())

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        cleaned = text.strip()
        return ParseResult(
            matched=True,
            effect=UnparsedOracleEffect(
                raw_text=cleaned,
                hints=_detect_hints(cleaned),
                heuristic_kind=_detect_kind(cleaned),
            ),
            consumed_text=cleaned,
        )
