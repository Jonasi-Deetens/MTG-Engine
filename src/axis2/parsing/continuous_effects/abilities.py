# axis2/parsing/continuous_effects/abilities.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from .patterns import HAS_ABILITY_RE, GAINS_ABILITY_RE, ABILITY_KEYWORDS
from axis2.schema import ContinuousEffect, GrantedAbility, ParseContext
from axis2.parsing.layers import assign_layer_to_effect
import re

class AbilitiesParser(ContinuousEffectParser):
    """Parses ability granting effects: 'has flying', 'gains haste'"""
    priority = 50  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return "has " in lower or "gains " in lower or "gain " in lower

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()

        # Extract the part after "has ..." or "gains ..."
        if "has " in lower:
            m = HAS_ABILITY_RE.search(lower)
            if not m:
                return ParseResult(matched=False)
            ability_part = m.group(1)
        elif "gains " in lower or "gain " in lower:
            m = GAINS_ABILITY_RE.search(lower)
            if not m:
                return ParseResult(matched=False)
            ability_part = m.group(1)
        else:
            return ParseResult(matched=False)

        # Normalize separators
        ability_part = ability_part.replace(", and ", ", ")
        ability_part = ability_part.replace(" and ", ", ")
        raw = [a.strip().rstrip(".") for a in ability_part.split(",")]

        abilities: list[GrantedAbility] = []

        for a in raw:
            a_clean = re.sub(r"\s+until.*$", "", a).strip().lower()

            # Ward {N}
            m = re.match(r"ward\s*\{(\d+)\}", a_clean)
            if m:
                value = int(m.group(1))
                abilities.append(GrantedAbility(kind="ward", value=value))
                continue

            # Simple keyword abilities - check exact match
            if a_clean in ABILITY_KEYWORDS:
                abilities.append(GrantedAbility(kind=a_clean))
                continue
            
            # Try matching against keywords - check if ability text contains or matches keyword
            for keyword in ABILITY_KEYWORDS:
                if a_clean == keyword or a_clean.strip() == keyword:
                    abilities.append(GrantedAbility(kind=keyword))
                    break

        if not abilities:
            return ParseResult(matched=False)

        effect = ContinuousEffect(
            kind="grant_ability",
            applies_to=applies_to,
            abilities=abilities,
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

