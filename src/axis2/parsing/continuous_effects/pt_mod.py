# axis2/parsing/continuous_effects/pt_mod.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from .patterns import PT_GETS_RE, BASE_PT_RE, FOR_EACH_COUNTER_RE
from axis2.schema import ContinuousEffect, PTExpression, ParseContext, DynamicValue
from axis2.parsing.subject import subject_from_text
from axis2.parsing.layers import assign_layer_to_effect

def parse_dynamic_counter_clause(text: str, ctx: ParseContext):
    """Parse dynamic counter clause like 'for each valor counter on this creature'"""
    m = FOR_EACH_COUNTER_RE.search(text)
    if not m:
        return None

    counter_type = m.group("counter").lower().strip()
    subj_text = m.group("subject").strip()

    # Convert subject text ("this creature") into a Subject object
    subject = subject_from_text(subj_text, ctx)

    return DynamicValue(
        kind="counter_count",
        counter_type=counter_type,
        subject=subject
    )

class PTParser(ContinuousEffectParser):
    """Parses P/T modification effects: 'gets +3/+3'"""
    priority = 60  # High priority - P/T mods are common

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY - no regex, no parsing
        # Reject trigger text - continuous effects don't start with "when" or "whenever"
        text_lower = text.strip().lower()
        if text_lower.startswith(("when ", "whenever ", "at ")):
            return False
        return "gets" in text_lower and "/" in text

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        m = PT_GETS_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            p = m.group(1).lstrip("+")
            t = m.group(2).lstrip("+")
            pt = PTExpression(power=p, toughness=t)

            effect = ContinuousEffect(
                kind="pt_mod",
                applies_to=applies_to,
                pt_value=pt,
                condition=condition,
                text=text,
                duration=duration,
                layer=7,  # Will be overridden by assign_layer_to_effect, but set default
                sublayer="7c",
            )

            # Detect dynamic scaling like "for each valor counter on this creature"
            dynamic = parse_dynamic_counter_clause(text, ctx)
            if dynamic:
                effect.dynamic = dynamic

            # Assign layer and sublayer
            assign_layer_to_effect(effect)

            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,  # We recognized the pattern, but parsing failed
                errors=[f"Failed to parse P/T mod: {e}"]
            )


class BasePTParser(ContinuousEffectParser):
    """Parses base P/T setting effects: 'with base power and toughness 3/3'"""
    priority = 55  # Slightly lower than P/T mod

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "base power" in text.lower() and "toughness" in text.lower()

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        m = BASE_PT_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            pt = PTExpression(power=m.group(1), toughness=m.group(2))

            effect = ContinuousEffect(
                kind="pt_set",
                applies_to=applies_to,
                pt_value=pt,
                condition=condition,
                text=text,
                duration=duration,
                layer=7,  # Will be overridden by assign_layer_to_effect, but set default
                sublayer="7b",
            )

            # Assign layer and sublayer
            assign_layer_to_effect(effect)

            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse base P/T: {e}"]
            )

