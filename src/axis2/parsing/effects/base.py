# axis2/parsing/effects/base.py

from typing import Protocol, Optional, List
from dataclasses import dataclass, field
from axis2.schema import Effect, ParseContext

# NOTE: ParseContext should have current_effect_text field for diagnostics
# This gives us:
# - Error reports with context
# - Better test failure messages  
# - Easier AST migration later
# 
# If ParseContext doesn't have this yet, we'll need to add it or create
# a wrapper that includes it.

@dataclass
class ParseResult:
    """Standardized return type for all parsers"""
    matched: bool = False  # Explicit intent: did parser recognize this pattern?
    effect: Optional[Effect] = None
    effects: Optional[List[Effect]] = None  # For parsers that return multiple
    consumed_text: Optional[str] = None  # Text that was parsed
    # NOTE: consumed_text may later be a substring once partial parsing / 
    # remainder parsing is supported. Currently it's the full text, but 
    # parsers that consume only part of the input will set it to the consumed portion.
    errors: Optional[List[str]] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        """
        Success means: parser matched AND produced valid effect(s) AND no errors.
        
        This allows for:
        - matched=True, effect=None, errors=[...] → "recognized but invalid"
        - matched=False → "didn't recognize this pattern"
        - matched=True, effect=Effect, errors=[] → "success"
        """
        return self.matched and len(self.errors) == 0 and \
               (self.effect is not None or 
                (self.effects is not None and len(self.effects) > 0))
    
    @property
    def all_effects(self) -> List[Effect]:
        """Returns all effects as a list"""
        result = []
        if self.effect:
            result.append(self.effect)
        if self.effects:
            result.extend(self.effects)
        return result

class EffectParser(Protocol):
    """Interface all effect parsers must implement"""
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
        - Simple keyword checks: "damage" in text.lower()
        - Basic string operations
        - Fast boolean logic
        
        This is called for EVERY parser on EVERY text, so performance matters.
        """
        ...
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """Parse the text, return ParseResult"""
        ...

