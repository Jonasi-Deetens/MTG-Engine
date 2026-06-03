# axis2/parsing/keyword_abilities/hidden_agenda.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class HiddenAgendaParser:
    """Parses Hidden Agenda keyword ability (static ability for conspiracy cards)"""
    
    keyword_name = "hidden agenda"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Hidden Agenda pattern"""
        lower = reminder_text.lower()
        return "command zone" in lower and "face down" in lower and "secretly name" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Hidden Agenda reminder text"""
        logger.debug(f"[HiddenAgendaParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "command zone" not in lower or "face down" not in lower:
            return []
        
        logger.debug(f"[HiddenAgendaParser] Detected Hidden Agenda")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Hidden Agenda keyword without reminder text"""
        logger.debug(f"[HiddenAgendaParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[HiddenAgendaParser] Detected Hidden Agenda")
        
        return []

