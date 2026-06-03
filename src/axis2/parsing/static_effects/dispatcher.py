# axis2/parsing/static_effects/dispatcher.py

from typing import List
from .base import ParseResult
from .registry import get_registry
from axis2.schema import StaticEffect, ParseContext, DayboundEffect, NightboundEffect
from axis2.parsing.text_extraction import get_remaining_text_for_parsing
from axis2.parsing.layers import parse_static_layer
import logging

logger = logging.getLogger(__name__)

def parse_static_effects(axis1_face, ctx: ParseContext) -> List[StaticEffect]:
    """
    Main entry point - combines Axis1 static effects with Axis2-detected static effects.
    """
    effects = []

    # ------------------------------------------------------------
    # 1. Axis1-provided static effects
    # ------------------------------------------------------------
    raw_effects = getattr(axis1_face, "static_effects", [])
    for raw in raw_effects:
        layer_str = raw.get("layering", "rules")
        layer, sublayer = parse_static_layer(layer_str)
        effects.append(
            StaticEffect(
                kind=raw["kind"],
                subject=raw["subject"],
                value=raw["value"],
                layer=layer,
                sublayer=sublayer,
                zones=raw["zones"],
            )
        )

    # ------------------------------------------------------------
    # 2. Axis2-detected static effects from oracle text
    # ------------------------------------------------------------
    # Use cleaned_oracle_text which now delegates to get_remaining_text_for_parsing
    from axis2.helpers import cleaned_oracle_text
    text = cleaned_oracle_text(axis1_face)

    # Daybound / Nightbound (special cases)
    if "daybound" in text:
        effects.append(DayboundEffect())

    if "nightbound" in text:
        effects.append(NightboundEffect())

    # Use registry to parse general static effects
    effects.extend(parse_general_static_effects(text, ctx))

    return effects

def parse_general_static_effects(text: str, ctx: ParseContext) -> List[StaticEffect]:
    """
    Parse general static effects from text using registry.
    """
    effects = []
    if not text:
        return effects

    registry = get_registry()

    # Try timing override first (special case)
    t = text.lower()
    if "as though they had flash" in t or "as though it had flash" in t:
        from axis2.schema import Subject
        layer, sublayer = parse_static_layer("rules")
        effects.append(
            StaticEffect(
                kind="timing_override",
                subject=Subject(
                    scope="self",
                    controller="you",
                    types=["spell"],
                    filters={}
                ),
                value={"as_flash": True},
                layer=layer,
                sublayer=sublayer,
                zones=["hand", "stack"],
            )
        )

    # Use registry for other static effects
    result = registry.parse(text, ctx)
    if result.is_success:
        effects.extend(result.all_effects)
    else:
        logger.warning(f"Failed to parse static effect: {text[:50]}...")
        if result.errors:
            logger.debug(f"Errors: {result.errors}")

    return effects

