# axis2/parsing/keyword_abilities/daybound.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect, DayboundEffect, NightboundEffect

logger = logging.getLogger(__name__)


class DayboundParser:
    """Parses Daybound keyword ability (static ability)"""
    
    keyword_name = "daybound"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Daybound pattern"""
        lower = reminder_text.lower()
        return "becomes night" in lower or "cast no spells" in lower or "day" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Daybound reminder text"""
        logger.debug(f"[DayboundParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "day" not in lower and "night" not in lower:
            return []
        
        daybound_effect = DayboundEffect()
        
        logger.debug(f"[DayboundParser] Created DayboundEffect for Daybound")
        
        return [daybound_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Daybound keyword without reminder text"""
        logger.debug(f"[DayboundParser] Parsing keyword only: {keyword_text}")
        
        daybound_effect = DayboundEffect()
        
        logger.debug(f"[DayboundParser] Created DayboundEffect for Daybound")
        
        return [daybound_effect]


class NightboundParser:
    """Parses Nightbound keyword ability (static ability)"""
    
    keyword_name = "nightbound"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Nightbound pattern"""
        lower = reminder_text.lower()
        return "becomes day" in lower or "cast at least two spells" in lower or "night" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Nightbound reminder text"""
        logger.debug(f"[NightboundParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "day" not in lower and "night" not in lower:
            return []
        
        nightbound_effect = NightboundEffect()
        
        logger.debug(f"[NightboundParser] Created DayboundEffect for Nightbound")
        
        return [nightbound_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Nightbound keyword without reminder text"""
        logger.debug(f"[NightboundParser] Parsing keyword only: {keyword_text}")
        
        nightbound_effect = DayboundEffect()
        
        logger.debug(f"[NightboundParser] Created DayboundEffect for Nightbound")
        
        return [nightbound_effect]

