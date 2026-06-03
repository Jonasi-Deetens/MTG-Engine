# axis2/parsing/keyword_abilities/ascend.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import StaticEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class AscendParser:
    """Parses Ascend keyword ability (static ability)"""
    
    keyword_name = "ascend"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Ascend pattern"""
        lower = reminder_text.lower()
        return "control ten or more permanents" in lower and "city's blessing" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ascend reminder text into StaticEffect"""
        logger.debug(f"[AscendParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "control ten or more permanents" not in lower or "city's blessing" not in lower:
            return []
        
        static_effect = StaticEffect(
            kind="grant_designation",
            subject=Subject(scope="you"),
            value={"designation": "citys_blessing", "condition": "control_ten_or_more_permanents"},
            layer=1,
            zones=["battlefield"]
        )
        
        logger.debug(f"[AscendParser] Created StaticEffect for Ascend")
        
        return [static_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ascend keyword without reminder text"""
        logger.debug(f"[AscendParser] Parsing keyword only: {keyword_text}")
        
        static_effect = StaticEffect(
            kind="grant_designation",
            subject=Subject(scope="you"),
            value={"designation": "citys_blessing", "condition": "control_ten_or_more_permanents"},
            layer=1,
            zones=["battlefield"]
        )
        
        logger.debug(f"[AscendParser] Created StaticEffect for Ascend")
        
        return [static_effect]

