# axis2/parsing/continuous_effects/base.py

from typing import Protocol, Optional, List
from dataclasses import dataclass, field
from axis2.schema import ContinuousEffect, ParseContext

@dataclass
class ParseResult:
    """Standardized return type for all continuous effect parsers"""
    matched: bool = False  # Explicit intent: did parser recognize this pattern?
    effect: Optional[ContinuousEffect] = None
    effects: Optional[List[ContinuousEffect]] = None  # For parsers that return multiple
    consumed_text: Optional[str] = None  # Text that was parsed
    errors: Optional[List[str]] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        """
        Success means: parser matched AND produced valid effect(s) AND no errors.
        
        This allows for:
        - matched=True, effect=None, errors=[...] → "recognized but invalid"
        - matched=False → "didn't recognize this pattern"
        - matched=True, effect=ContinuousEffect, errors=[] → "success"
        """
        return self.matched and len(self.errors) == 0 and \
               (self.effect is not None or 
                (self.effects is not None and len(self.effects) > 0))
    
    @property
    def all_effects(self) -> List[ContinuousEffect]:
        """Returns all effects as a list"""
        result = []
        if self.effect:
            result.append(self.effect)
        if self.effects:
            result.extend(self.effects)
        return result

class ContinuousEffectParser(Protocol):
    """Interface all continuous effect parsers must implement"""
    priority: int  # Higher = tried first
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        """
        Quick check if this parser might match.
        
        ⚠️ CRITICAL: This must be CHEAP - no expensive operations!
        
        MUST NOT:
        - Run regex with groups
        - Call subject parsing
        - Allocate schema objects
        - Do any actual parsing work
        
        SHOULD:
        - Simple keyword checks: "gets" in text.lower()
        - Basic string operations
        - Fast boolean logic
        
        This is called for EVERY parser on EVERY text, so performance matters.
        """
        ...
    
    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None, 
              condition=None, duration: Optional[str] = None) -> ParseResult:
        """
        Parse the text, return ParseResult.
        
        Args:
            text: The clause text to parse
            ctx: Parse context
            applies_to: The subject this effect applies to (from previous clause)
            condition: Condition for this effect (from previous parsing)
            duration: Duration for this effect (from previous parsing)
        """
        ...

