# axis2/parsing/continuous_effects/loss_effects.py

from typing import Optional, List
from .base import ContinuousEffectParser, ParseResult
from .patterns import LOSES_ALL_RE
from axis2.schema import ContinuousEffect, ParseContext

class LossEffectsParser(ContinuousEffectParser):
    """Parses ability/type loss effects: 'loses all abilities'"""
    priority = 25  # Lower priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return "loses" in lower and ("abilities" in lower or "card types" in lower or "creature types" in lower)

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()
        effects: List[ContinuousEffect] = []

        # Lose all abilities (keep this as-is, it's precise and good)
        if "loses all abilities" in lower or "loses all other abilities" in lower:
            effects.append(
                ContinuousEffect(
                    kind="ability_remove_all",
                    applies_to=applies_to,
                    condition=condition,
                    text=text,
                )
            )

        # Lose card types if they appear in the same clause
        if "card types" in lower:
            effects.append(
                ContinuousEffect(
                    kind="type_remove_all",
                    applies_to=applies_to,
                    condition=condition,
                    text=text,
                )
            )

        # Lose creature types if they appear in the same clause
        if "creature types" in lower:
            effects.append(
                ContinuousEffect(
                    kind="subtype_remove_all",
                    applies_to=applies_to,
                    condition=condition,
                    text=text,
                )
            )

        if not effects:
            return ParseResult(matched=False)

        return ParseResult(
            matched=True,
            effects=effects,
            consumed_text=text
        )

