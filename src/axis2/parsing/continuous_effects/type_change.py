# axis2/parsing/continuous_effects/type_change.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from axis2.schema import ContinuousEffect, TypeChangeData, ParseContext
from axis2.parsing.layers import assign_layer_to_effect

class TypeChangeParser(ContinuousEffectParser):
    """Parses type change effects: 'is a creature', 'is an artifact creature'"""
    priority = 40  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return (" is a " in lower or " is an " in lower or " is " in lower) and \
               any(t in lower for t in ["creature", "artifact", "enchantment", "land", "planeswalker", "instant", "sorcery"])

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()
        if " is a " in lower:
            after = lower.split(" is a ", 1)[1]
        elif " is an " in lower:
            after = lower.split(" is an ", 1)[1]
        elif " is " in lower:
            after = lower.split(" is ", 1)[1]
        else:
            return ParseResult(matched=False)

        # Stop at common clause boundaries
        for stop in [" with base power", " and has ", " and it loses", " and loses "]:
            idx = after.find(stop)
            if idx != -1:
                after = after[:idx]
                break

        after = after.strip(" ,.")
        words = after.split()

        known_types = {"creature", "artifact", "enchantment", "land", "planeswalker", "instant", "sorcery"}
        types = [w for w in words if w in known_types]
        # everything else we treat as subtypes for now
        subtypes = [w for w in words if w not in known_types]

        if not types and not subtypes:
            return ParseResult(matched=False)

        # you might want separate fields later; for now, pack them
        type_change = TypeChangeData(set_types=types + subtypes)

        effect = ContinuousEffect(
            kind="type_set",
            applies_to=applies_to,
            type_change=type_change,
            condition=condition,
            text=text,
            duration=duration,
            layer=4,  # Will be overridden by assign_layer_to_effect, but set default
        )

        # Assign layer and sublayer
        assign_layer_to_effect(effect)

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

