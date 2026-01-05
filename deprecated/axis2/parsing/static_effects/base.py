# axis2/parsing/static_effects/base.py

from typing import Protocol, Optional, List
from dataclasses import dataclass, field
from axis2.schema import StaticEffect, ParseContext

@dataclass
class ParseResult:
    """Standardized return type for all static effect parsers"""
    matched: bool = False  # Explicit intent: did parser recognize this pattern?
    effect: Optional[StaticEffect] = None
    effects: Optional[List[StaticEffect]] = None  # For parsers that return multiple
    consumed_text: Optional[str] = None  # Text that was parsed
    errors: Optional[List[str]] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        """
        Success means: parser matched AND produced valid effect(s) AND no errors.
        """
        return self.matched and len(self.errors) == 0 and \
               (self.effect is not None or 
                (self.effects is not None and len(self.effects) > 0))
    
    @property
    def all_effects(self) -> List[StaticEffect]:
        """Returns all effects as a list"""
        result = []
        if self.effect:
            result.append(self.effect)
        if self.effects:
            result.extend(self.effects)
        return result

class StaticEffectParser(Protocol):
    """Interface all static effect parsers must implement"""
    priority: int  # Higher = tried first
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        """
        Quick check if this parser might match.
        
        ⚠️ CRITICAL: This must be CHEAP - no expensive operations!
        """
        ...
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """Parse the text, return ParseResult"""
        ...

