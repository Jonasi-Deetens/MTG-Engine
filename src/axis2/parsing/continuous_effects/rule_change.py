# axis2/parsing/continuous_effects/rule_change.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from axis2.schema import ContinuousEffect, RuleChangeData, ParseContext
from axis2.parsing.layers import assign_layer_to_effect
import re

class RuleChangeParser(ContinuousEffectParser):
    """Parses rule-changing continuous effects: 'must choose at least one flagbearer'"""
    priority = 30  # Lower priority - rule changes are less common

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return "must choose" in lower or "flagbearer" in lower

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()

        # Coalition Flag / Flagbearer pattern
        if "must choose at least one flagbearer" in lower:
            rule_change = RuleChangeData(
                kind="targeting_requirement",
                requires_flagbearer=True,
                controller="opponent"
            )
        # Generalized "must choose this creature if able"
        elif "must choose" in lower and "if able" in lower:
            # Generalized "must choose a creature with X"
            m = re.search(r"must choose .* (creature.*) if able", lower)
            if m:
                rule_change = RuleChangeData(
                    kind="targeting_requirement",
                    requires_filter=m.group(1)
                )
            else:
                rule_change = RuleChangeData(
                    kind="targeting_requirement",
                    requires_this=True
                )
        else:
            return ParseResult(matched=False)

        effect = ContinuousEffect(
            kind="rule_change",
            applies_to=None,
            rule_change=rule_change,
            condition=condition,
            text=text,
            duration=duration,
            layer=6,  # Will be overridden by assign_layer_to_effect, but set default
        )

        # Assign layer and sublayer
        assign_layer_to_effect(effect)

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

