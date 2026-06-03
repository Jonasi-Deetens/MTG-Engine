# axis2/parsing/effects/casting_permission.py

import re
from typing import Optional
from .base import EffectParser, ParseResult
from axis2.schema import ParseContext, GrantCastingPermissionEffect

# Pattern: "you may cast [a/an] [type] spell[s] from [zone] [duration]"
# Examples:
# - "you may cast a creature spell from that player's graveyard this turn"
# - "you may cast spells from your graveyard"
# - "you may cast a creature spell from that player's graveyard this turn, and you may spend mana as though it were mana of any color to cast that spell"
CAST_PERMISSION_RE = re.compile(
    r"you\s+may\s+cast\s+(?:a|an|any\s+number\s+of)?\s*"
    r"([^,]+?)\s+spell(?:s)?\s+from\s+"
    r"(?:that\s+player'?s?|your|an?\s+opponent'?s?|each\s+opponent'?s?)\s+"
    r"(graveyard|exile|library|hand|command)",
    re.IGNORECASE | re.DOTALL
)

# Pattern: "spend mana as though it were mana of any color"
MANA_ANY_COLOR_RE = re.compile(
    r"spend\s+mana\s+as\s+though\s+it\s+were\s+mana\s+of\s+any\s+color",
    re.IGNORECASE
)

# Pattern: "this turn" or "until end of turn"
DURATION_RE = re.compile(
    r"(?:this\s+turn|until\s+end\s+of\s+turn)",
    re.IGNORECASE
)


class CastingPermissionParser(EffectParser):
    """
    Parser for effects that grant permission to cast spells from specific zones.
    
    Examples:
    - "you may cast a creature spell from that player's graveyard this turn"
    - "you may cast spells from your graveyard"
    - "you may cast a creature spell from that player's graveyard this turn, and you may spend mana as though it were mana of any color to cast that spell"
    """
    
    priority = 60  # High priority - specific pattern
    
    def can_parse(self, text: str, ctx: Optional[ParseContext] = None) -> bool:
        """Check if text contains casting permission pattern."""
        text_lower = text.lower()
        return "you may cast" in text_lower and ("from" in text_lower or "graveyard" in text_lower or "exile" in text_lower)
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """Parse casting permission effect."""
        text = text.strip()
        
        # Handle compound sentences - split on "and" or comma, but keep the full text for matching
        # The regex will match the first part, and we'll check the full text for mana modification
        full_text = text
        
        # Try to match the main pattern
        m = CAST_PERMISSION_RE.search(text)
        if not m:
            return ParseResult(matched=False, errors=[f"Could not match casting permission pattern: {text[:50]}..."])
        
        spell_description = m.group(1).strip()
        from_zone = m.group(2).lower()
        
        # Parse spell filter from description
        spell_filter = {}
        
        # Extract types (e.g., "creature", "instant", "sorcery")
        type_keywords = ["creature", "instant", "sorcery", "artifact", "enchantment", "planeswalker", "land"]
        found_types = []
        for t in type_keywords:
            if t in spell_description.lower():
                found_types.append(t)
        if found_types:
            spell_filter["types"] = found_types
        
        # Extract controller scope from the full text
        text_lower = full_text.lower()
        if "that player" in text_lower or "that player's" in text_lower:
            spell_filter["controller"] = "that_player"
        elif "your" in text_lower:
            spell_filter["controller"] = "you"
        elif "opponent" in text_lower:
            spell_filter["controller"] = "opponent"
        
        # Check for duration in the full text
        duration = "permanent"  # Default
        if DURATION_RE.search(full_text):
            duration = "this_turn"
        
        # Check for mana modification in the full text
        mana_modification = None
        if MANA_ANY_COLOR_RE.search(full_text):
            mana_modification = "any_color"
        
        effect = GrantCastingPermissionEffect(
            from_zone=from_zone,
            spell_filter=spell_filter,
            duration=duration,
            mana_modification=mana_modification
        )
        
        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

