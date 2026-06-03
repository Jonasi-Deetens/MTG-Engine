# axis2/parsing/effects/conditional_mana.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import AddManaEffect, ParseContext
from axis2.parsing.conditions import parse_control_condition

# Pattern for "If condition, add X instead" within effect text
# Example: "If you control an Urza's Power-Plant and an Urza's Tower, add {C}{C} instead"
CONDITIONAL_MANA_REPLACEMENT_RE = re.compile(
    r"if\s+(.+?),\s+add\s+((?:\{[^}]+\})+)\s+instead",
    re.IGNORECASE
)

# Pattern for base mana effect followed by conditional replacement
# Example: "Add {C}. If you control..., add {C}{C} instead"
BASE_AND_REPLACEMENT_RE = re.compile(
    r"add\s+((?:\{[^}]+\})+)\s*\.\s*if\s+(.+?),\s+add\s+((?:\{[^}]+\})+)\s+instead",
    re.IGNORECASE | re.DOTALL
)

class ConditionalManaParser(EffectParser):
    """
    Parses conditional mana replacement effects within activated abilities.
    
    Handles patterns like:
    - "Add {C}. If you control an Urza's Power-Plant and an Urza's Tower, add {C}{C} instead"
    """
    priority = 70  # High priority - very specific pattern
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        text_lower = text.lower()
        return "add" in text_lower and "if" in text_lower and "instead" in text_lower
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """
        Parse conditional mana replacement effects.
        
        Returns AddManaEffect with condition and replacement_mana fields set.
        """
        try:
            # Try to match the full pattern: "Add {X}. If condition, add {Y} instead"
            m = BASE_AND_REPLACEMENT_RE.search(text)
            if m:
                base_mana_text = m.group(1).strip()
                condition_text = m.group(2).strip()
                replacement_mana_text = m.group(3).strip()
                
                # Extract mana symbols
                base_symbols = re.findall(r"\{[^}]+\}", base_mana_text)
                replacement_symbols = re.findall(r"\{[^}]+\}", replacement_mana_text)
                
                # Parse condition into structured object
                condition_obj = parse_control_condition(condition_text)
                
                return ParseResult(
                    matched=True,
                    effect=AddManaEffect(
                        mana=base_symbols,
                        choice=None,
                        condition=condition_text,  # Keep string for backward compatibility
                        condition_obj=condition_obj,  # Structured condition
                        replacement_mana=replacement_symbols
                    ),
                    consumed_text=text
                )
            
            # Fallback: Just the replacement part (if base was already parsed)
            # This handles cases where the text is split: "If condition, add {X} instead"
            m = CONDITIONAL_MANA_REPLACEMENT_RE.search(text)
            if m:
                condition_text = m.group(1).strip()
                replacement_mana_text = m.group(2).strip()
                replacement_symbols = re.findall(r"\{[^}]+\}", replacement_mana_text)
                
                # This is a replacement-only effect - we need the base effect from context
                # For now, return an effect that indicates this is a replacement
                # The dispatcher should handle combining this with the base effect
                
                # Parse condition into structured object
                condition_obj = parse_control_condition(condition_text)
                
                return ParseResult(
                    matched=True,
                    effect=AddManaEffect(
                        mana=[],  # Base will be set by combining logic
                        choice=None,
                        condition=condition_text,  # Keep string for backward compatibility
                        condition_obj=condition_obj,  # Structured condition
                        replacement_mana=replacement_symbols
                    ),
                    consumed_text=text
                )
            
            return ParseResult(matched=False)
        except Exception as e:
            return ParseResult(
                matched=False,
                errors=[f"Failed to parse conditional mana replacement: {e}"]
            )

