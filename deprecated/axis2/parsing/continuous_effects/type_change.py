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
        
        # Don't match replacement effect patterns - these should be handled by replacement parsers
        if "damage would be dealt" in lower and "instead" in lower:
            return False
        if "would be" in lower and "instead" in lower:
            return False
        
        return (" is a " in lower or " is an " in lower or " is " in lower) and \
               any(t in lower for t in ["creature", "artifact", "enchantment", "land", "planeswalker", "instant", "sorcery"])

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()
        
        # Don't match replacement effect patterns - these should be handled by replacement parsers
        if "damage would be dealt" in lower and "instead" in lower:
            return ParseResult(matched=False)
        if "would be" in lower and "instead" in lower:
            return ParseResult(matched=False)
        
        # Don't match "is dealt to" - this is damage redirection, not type setting
        if " is dealt to" in lower or " is dealt " in lower:
            return ParseResult(matched=False)
        
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


class TypeRemovalParser(ContinuousEffectParser):
    """Parses type removal effects: 'isn't a creature until...' (Impending)"""
    priority = 45  # Higher than TypeChangeParser to catch "isn't" before "is"
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return ("isn't" in lower or "is not" in lower) and "creature" in lower
    
    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()
        
        # Pattern: "isn't a creature until..." or "is not a creature until..."
        if "isn't" in lower:
            after = lower.split("isn't", 1)[1]
        elif "is not" in lower:
            after = lower.split("is not", 1)[1]
        else:
            return ParseResult(matched=False)
        
        # Extract the type being removed (usually "creature")
        types_to_remove = []
        if "creature" in after:
            types_to_remove.append("creature")
        # Could add more types here if needed
        
        if not types_to_remove:
            return ParseResult(matched=False)
        
        # Extract condition from "until..." clause
        # Use passed condition if available, otherwise parse from text
        condition_text = condition
        if not condition_text and "until" in after:
            until_part = after.split("until", 1)[1].strip()
            # For Impending: "until the last is removed" means "while time counters > 0"
            if "last is removed" in until_part or "last time counter is removed" in until_part:
                condition_text = "time_counters > 0"
            # Could add more condition parsing here
        
        type_change = TypeChangeData(
            set_types=None,
            add_types=None,
            remove_types=types_to_remove
        )
        
        effect = ContinuousEffect(
            kind="type_remove",
            applies_to=applies_to or "self",
            type_change=type_change,
            condition=condition_text,
            text=text,
            duration=duration,
            layer=4,  # Type changes are layer 4
        )
        
        # Assign layer and sublayer
        assign_layer_to_effect(effect)
        
        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )