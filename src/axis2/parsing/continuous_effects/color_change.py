# axis2/parsing/continuous_effects/color_change.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from .patterns import IS_COLOR_RE, COLOR_WORD_TO_SYMBOL
from axis2.schema import ContinuousEffect, ColorChangeData, ParseContext
from axis2.parsing.layers import assign_layer_to_effect

class ColorChangeParser(ContinuousEffectParser):
    """Parses color change effects: 'is red', 'is all colors'"""
    priority = 45  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return "is " in lower and ("color" in lower or any(c in lower for c in ["white", "blue", "black", "red", "green"]))

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()

        if "is all colors" in lower:
            color_change = ColorChangeData(set_colors=["W", "U", "B", "R", "G"])
        else:
            m = IS_COLOR_RE.search(lower)
            if not m:
                return ParseResult(matched=False)

            words = m.group(1).replace(",", " ").split()
            colors = [COLOR_WORD_TO_SYMBOL[w] for w in words if w in COLOR_WORD_TO_SYMBOL]
            if not colors:
                return ParseResult(matched=False)

            if "in addition to its other colors" in lower:
                color_change = ColorChangeData(add_colors=colors)
            else:
                color_change = ColorChangeData(set_colors=colors)

        effect = ContinuousEffect(
            kind="color_set" if color_change.set_colors else "color_add",
            applies_to=applies_to,
            color_change=color_change,
            condition=condition,
            text=text,
            duration=duration,
            layer=5,  # Will be overridden by assign_layer_to_effect, but set default
        )

        # Assign layer and sublayer
        assign_layer_to_effect(effect)

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

