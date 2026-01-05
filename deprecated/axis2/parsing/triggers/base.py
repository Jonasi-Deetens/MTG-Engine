# axis2/parsing/triggers/base.py

from typing import Protocol, Optional, Union
from dataclasses import dataclass, field
from axis2.schema import (
    ZoneChangeEvent, DealsDamageEvent, EntersBattlefieldEvent,
    LeavesBattlefieldEvent, CastSpellEvent
)

@dataclass
class ParseResult:
    """Standardized return type for all trigger parsers"""
    matched: bool = False
    event: Optional[Union[ZoneChangeEvent, DealsDamageEvent, EntersBattlefieldEvent, 
                          LeavesBattlefieldEvent, CastSpellEvent, str]] = None
    errors: Optional[list] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        return self.matched and len(self.errors) == 0 and self.event is not None

class TriggerParser(Protocol):
    """Interface all trigger parsers must implement"""
    priority: int
    
    def can_parse(self, text: str) -> bool:
        """Quick check if this parser might match. Must be CHEAP."""
        ...
    
    def parse(self, text: str) -> ParseResult:
        """Parse the text, return ParseResult"""
        ...

