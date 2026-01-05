# axis2/parsing/replacement_effects/mana_replacement.py

import re
from .base import ReplacementEffectParser, ParseResult
from axis2.schema import ReplacementEffect, Subject
from axis2.parsing.effects.mana import ADD_MANA_FIXED_RE

# Pattern for "If condition, add X instead" (no "would")
# Example: "If you control an Urza's Power-Plant and an Urza's Tower, add {C}{C} instead"
RE_MANA_REPLACEMENT = re.compile(
    r"if\s+(.+?),\s+add\s+((?:\{[^}]+\})+)\s+instead",
    re.IGNORECASE
)

class ManaReplacementParser(ReplacementEffectParser):
    """Parses replacement effects for mana abilities: 'If condition, add X instead'"""
    priority = 60  # High priority - specific pattern
    
    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "if" in text.lower() and "add" in text.lower() and "instead" in text.lower()
    
    def parse(self, text: str) -> ParseResult:
        """
        Parse replacement effects like:
        - "If you control an Urza's Power-Plant and an Urza's Tower, add {C}{C} instead"
        """
        try:
            m = RE_MANA_REPLACEMENT.search(text)
            if not m:
                return ParseResult(matched=False)
            
            condition_text = m.group(1).strip()
            mana_text = m.group(2).strip()
            
            # Extract mana symbols
            symbols = re.findall(r"\{[^}]+\}", mana_text)
            
            # Parse the condition - for now, store as text
            # TODO: Parse condition into structured format (control check, etc.)
            condition = {
                "type": "control_check",
                "text": condition_text
            }
            
            effect = ReplacementEffect(
                kind="mana_replacement",
                applies_to=None,  # Applies to the mana ability itself
                condition=condition,
                value={
                    "mana": symbols,
                    "instead": True
                }
            )
            
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except Exception as e:
            return ParseResult(
                matched=False,
                errors=[f"Failed to parse mana replacement: {e}"]
            )

