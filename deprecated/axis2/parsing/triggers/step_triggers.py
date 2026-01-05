# axis2/parsing/triggers/step_triggers.py

import re
from .base import TriggerParser, ParseResult

# Patterns for step triggers
BEGINNING_OF_UPKEEP_RE = re.compile(
    r"at\s+the\s+beginning\s+of\s+(?:your\s+|each\s+)?upkeep",
    re.IGNORECASE
)

BEGINNING_OF_END_STEP_RE = re.compile(
    r"at\s+the\s+beginning\s+of\s+(?:your\s+|each\s+player'?s?\s+)?end\s+step",
    re.IGNORECASE
)

BEGINNING_OF_DRAW_STEP_RE = re.compile(
    r"at\s+the\s+beginning\s+of\s+(?:your\s+|each\s+)?draw\s+step",
    re.IGNORECASE
)

BEGINNING_OF_COMBAT_RE = re.compile(
    r"at\s+the\s+beginning\s+of\s+(?:your\s+|each\s+)?combat",
    re.IGNORECASE
)

class StepTriggerParser(TriggerParser):
    """Parses step triggers: 'At the beginning of your upkeep', 'At the beginning of your end step', etc."""
    priority = 60  # High priority - specific patterns
    
    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return "at the beginning of" in lower and any(
            word in lower for word in ["upkeep", "end step", "draw step", "combat"]
        )
    
    def parse(self, text: str) -> ParseResult:
        """
        Parse step triggers and return event string.
        Returns: "upkeep", "end_step", "draw_step", "combat", etc.
        """
        try:
            lower = text.lower()
            
            # Check each pattern in order of specificity
            if BEGINNING_OF_END_STEP_RE.search(lower):
                return ParseResult(
                    matched=True,
                    event="end_step"
                )
            
            if BEGINNING_OF_UPKEEP_RE.search(lower):
                return ParseResult(
                    matched=True,
                    event="upkeep"
                )
            
            if BEGINNING_OF_DRAW_STEP_RE.search(lower):
                return ParseResult(
                    matched=True,
                    event="draw_step"
                )
            
            if BEGINNING_OF_COMBAT_RE.search(lower):
                return ParseResult(
                    matched=True,
                    event="combat"
                )
            
            return ParseResult(matched=False)
        except Exception as e:
            return ParseResult(
                matched=False,
                errors=[f"Failed to parse step trigger: {e}"]
            )

