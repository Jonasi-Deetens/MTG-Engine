# axis2/parsing/replacement_effects/counter_modification.py

import re
from .base import ReplacementEffectParser, ParseResult
from axis2.schema import ReplacementEffect, Subject

# Pattern for duration prefixes like "Until end of turn,"
DURATION_PREFIX_RE = re.compile(
    r"^(until\s+end\s+of\s+turn|this\s+turn|until\s+your\s+next\s+turn)[,\s]+",
    re.IGNORECASE
)

# Pattern for counter modification replacement effects
# "if you would put one or more +1/+1 counters on a creature you control, put that many plus one +1/+1 counters on it instead"
COUNTER_MODIFICATION_RE = re.compile(
    r"if\s+(?:you|a\s+player|an?\s+opponent)\s+would\s+put\s+(?:one\s+or\s+more|(\d+))\s+(\+?\d+/\+\d+|\w+)\s+counters?\s+on\s+(.+?),\s+put\s+that\s+many\s+(?:plus\s+(\d+)|minus\s+(\d+)|(\d+))\s+(\+?\d+/\+\d+|\w+)\s+counters?\s+on\s+it\s+instead",
    re.IGNORECASE
)

# Simpler pattern for "put that many plus one"
# Handles both "plus one" and "plus 1"
COUNTER_PLUS_ONE_RE = re.compile(
    r"if\s+(?:you|a\s+player|an?\s+opponent)\s+would\s+put\s+(?:one\s+or\s+more|(\d+))\s+(\+?\d+/\+\d+|\w+)\s+counters?\s+on\s+(.+?),\s+put\s+that\s+many\s+plus\s+(?:one|(\d+))\s+(\+?\d+/\+\d+|\w+)\s+counters?\s+on\s+it\s+instead",
    re.IGNORECASE
)

def _extract_duration(text: str) -> tuple[str, str | None]:
    """
    Extract duration prefix from text and return (remaining_text, duration).
    
    Returns:
        Tuple of (text_without_duration, duration_string_or_none)
    """
    m = DURATION_PREFIX_RE.match(text)
    if m:
        duration_text = m.group(1).lower()
        remaining = text[m.end():].strip()
        
        # Normalize duration
        if "until end of turn" in duration_text:
            duration = "until_end_of_turn"
        elif "this turn" in duration_text:
            duration = "this_turn"
        elif "until your next turn" in duration_text:
            duration = "until_your_next_turn"
        else:
            duration = None
            
        return remaining, duration
    
    return text, None

class CounterModificationParser(ReplacementEffectParser):
    """Parses counter modification replacement effects: 'if you would put counters, put that many plus one instead'"""
    priority = 50  # Medium-high priority
    
    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        # Check if it contains the key phrases, even with duration prefix
        return "would put" in lower and "counters" in lower and "instead" in lower
    
    def parse(self, text: str) -> ParseResult:
        """
        Parse counter modification replacement effects.
        
        Examples:
        - "if you would put one or more +1/+1 counters on a creature you control, put that many plus one +1/+1 counters on it instead"
        - "Until end of turn, if you would put one or more +1/+1 counters on a creature you control, put that many plus one +1/+1 counters on it instead"
        """
        try:
            # Extract duration prefix if present
            remaining_text, duration = _extract_duration(text)
            
            # IMPORTANT: If the original text had a duration prefix but we couldn't extract it,
            # or if duration is None but text clearly had a duration prefix, don't parse.
            # This prevents creating permanent replacement effects from temporary ability text.
            original_has_duration = DURATION_PREFIX_RE.search(text) is not None
            if original_has_duration and duration is None:
                # Text had duration prefix but extraction failed - this shouldn't happen,
                # but if it does, don't create an effect without duration
                return ParseResult(matched=False)
            
            # Try the simpler pattern first
            m = COUNTER_PLUS_ONE_RE.search(remaining_text)
            if m:
                counter_type = m.group(2).strip()  # e.g., "+1/+1"
                subject_text = m.group(3).strip()  # e.g., "a creature you control"
                # Handle both "one" and numeric digits
                extra_amount_str = m.group(4)  # Could be "one" or "1"
                if extra_amount_str:
                    extra_amount = int(extra_amount_str)
                else:
                    # Group 4 is None, meaning we matched "plus one" (word)
                    extra_amount = 1
                
                # Parse subject - handle "a creature you control" pattern
                from axis2.parsing.subject import subject_from_text
                from axis2.schema import Subject
                # Create a minimal context for subject parsing
                from axis2.schema import ParseContext
                minimal_ctx = ParseContext(
                    card_name="",
                    primary_type="",
                    face_name="",
                    face_types=[]
                )
                subject = subject_from_text(subject_text, minimal_ctx)
                
                # Fix subject for "a creature you control" pattern
                # The user wants scope='creature_you_control' for this specific pattern
                # If subject is still "self" but text contains "you control" and a type,
                # fix it to use the special scope value
                subject_lower = subject_text.lower()
                if (subject.scope == "self" and 
                    "you control" in subject_lower):
                    # Determine the type
                    types_list = []
                    scope_value = "each"  # Default to "each"
                    
                    if "creature" in subject_lower:
                        types_list = ["creature"]
                        scope_value = "creature_you_control"  # Special scope for "a creature you control"
                    elif "artifact" in subject_lower:
                        types_list = ["artifact"]
                    elif "enchantment" in subject_lower:
                        types_list = ["enchantment"]
                    elif "permanent" in subject_lower:
                        types_list = ["permanent"]
                    
                    # Create corrected subject
                    subject = Subject(
                        scope=scope_value,
                        controller="you",
                        types=types_list if types_list else None,
                        filters={}
                    )
                
                effect = ReplacementEffect(
                    kind="counter_modification",
                    event="put_counters",
                    subject=subject,
                    value={
                        "counter_type": counter_type,
                        "modification": "add_extra",
                        "extra_amount": extra_amount
                    },
                    zones=["battlefield"],
                    duration=duration  # Set duration if extracted
                )
                
                return ParseResult(
                    matched=True,
                    effect=effect,
                    consumed_text=text
                )
            
            # Try more complex pattern
            m = COUNTER_MODIFICATION_RE.search(remaining_text)
            if m:
                # This handles more complex cases - for now, use the simpler pattern above
                return ParseResult(matched=False)
            
            return ParseResult(matched=False)
        except Exception as e:
            return ParseResult(
                matched=False,
                errors=[f"Failed to parse counter modification replacement: {e}"]
            )

