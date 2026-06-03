# axis2/parsing/replacement_effects/base.py

from typing import Protocol, Optional, List
from dataclasses import dataclass, field
from axis2.schema import ReplacementEffect

@dataclass
class ParseResult:
    """Standardized return type for all replacement effect parsers"""
    matched: bool = False
    effect: Optional[ReplacementEffect] = None
    effects: Optional[List[ReplacementEffect]] = None
    consumed_text: Optional[str] = None
    errors: Optional[List[str]] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        return self.matched and len(self.errors) == 0 and \
               (self.effect is not None or 
                (self.effects is not None and len(self.effects) > 0))
    
    @property
    def all_effects(self) -> List[ReplacementEffect]:
        """Returns all effects as a list"""
        result = []
        if self.effect:
            result.append(self.effect)
        if self.effects:
            result.extend(self.effects)
        return result

class ReplacementEffectParser(Protocol):
    """Interface all replacement effect parsers must implement"""
    priority: int
    
    def can_parse(self, text: str) -> bool:
        """Quick check if this parser might match. Must be CHEAP."""
        ...
    
    def parse(self, text: str) -> ParseResult:
        """Parse the text, return ParseResult"""
        ...

