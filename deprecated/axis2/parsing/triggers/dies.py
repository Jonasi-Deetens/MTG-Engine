# axis2/parsing/triggers/dies.py

from .base import TriggerParser, ParseResult
from .patterns import DIES_RE
from axis2.schema import DiesEvent

class DiesParser(TriggerParser):
    priority = 36
    
    def can_parse(self, text: str) -> bool:
        return "dies" in text.lower() and ("when" in text.lower() or "whenever" in text.lower())
    
    def parse(self, text: str) -> ParseResult:
        m = DIES_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        
        try:
            event = DiesEvent(subject=m.group(1).strip())
            
            return ParseResult(
                matched=True,
                event=event
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse dies trigger: {e}"]
            )

