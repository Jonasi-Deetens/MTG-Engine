# axis2/parsing/static_effects/cost_modification.py

from typing import Optional
from .base import StaticEffectParser, ParseResult
from .patterns import COST_MOD_RE
from axis2.schema import StaticEffect, Subject, ParseContext
import re

class CostModificationParser(StaticEffectParser):
    """Parses cost modification effects: 'artifact spells you cast cost {1} less to cast'"""
    priority = 25  # Lower priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "spells" in text.lower() and "cast cost" in text.lower() and ("less" in text.lower() or "more" in text.lower())

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = COST_MOD_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            raw_types = m.group("types").strip()
            controller_word = m.group("controller")
            amount = int(m.group("amount"))
            direction = m.group("direction")

            # Determine controller
            controller = "you" if "you" in controller_word else "opponent"

            # Determine sign
            delta = -amount if direction == "less" else amount

            # Parse types (artifact, creature, instant and sorcery, etc.)
            types = []
            for part in re.split(r",|and", raw_types):
                p = part.strip()
                if p in ["artifact", "creature", "enchantment", "planeswalker", "instant", "sorcery", "noncreature"]:
                    types.append(p)
                elif p == "instant and sorcery":
                    types.extend(["instant", "sorcery"])
                elif p == "noncreature":
                    types.append("noncreature")

            # Build subject
            subject = Subject(
                scope="each",
                controller=controller,
                types=types + ["spell"],  # always spells
                filters={}
            )

            from axis2.parsing.layers import parse_static_layer
            layer, sublayer = parse_static_layer("cost_modification")
            effect = StaticEffect(
                kind="cost_modification",
                subject=subject,
                value={"generic": delta},
                layer=layer,
                sublayer=sublayer,
                zones=None
            )

            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse cost modification: {e}"]
            )

