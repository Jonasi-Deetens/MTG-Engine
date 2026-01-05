# axis2/parsing/keyword_abilities/base.py

from typing import Protocol, List, Optional
from axis2.schema import Effect, ParseContext


class KeywordAbilityParser(Protocol):
    """Protocol for keyword ability parsers"""
    
    keyword_name: str
    priority: int
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if this parser handles the reminder text"""
        ...
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse reminder text into Axis2 effects"""
        ...
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse keyword without reminder text (e.g., Ward {2})"""
        ...

