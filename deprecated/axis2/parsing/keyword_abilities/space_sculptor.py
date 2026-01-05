# axis2/parsing/keyword_abilities/space_sculptor.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import StaticEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class SpaceSculptorParser:
    """Parses Space Sculptor keyword ability (static ability)"""
    
    keyword_name = "space sculptor"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Space Sculptor pattern"""
        lower = reminder_text.lower()
        return "sector" in lower and ("alpha" in lower or "beta" in lower or "gamma" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Space Sculptor reminder text into StaticEffect"""
        logger.debug(f"[SpaceSculptorParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "sector" not in lower:
            return []
        
        static_effect = StaticEffect(
            kind="grant_designation",
            subject=Subject(scope="creatures_without_sector_designation"),
            value={"designation": "sector", "sectors": ["alpha", "beta", "gamma"]},
            layer=1,
            zones=["battlefield"]
        )
        
        logger.debug(f"[SpaceSculptorParser] Created StaticEffect for Space Sculptor")
        
        return [static_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Space Sculptor keyword without reminder text"""
        logger.debug(f"[SpaceSculptorParser] Parsing keyword only: {keyword_text}")
        
        static_effect = StaticEffect(
            kind="grant_designation",
            subject=Subject(scope="creatures_without_sector_designation"),
            value={"designation": "sector", "sectors": ["alpha", "beta", "gamma"]},
            layer=1,
            zones=["battlefield"]
        )
        
        logger.debug(f"[SpaceSculptorParser] Created StaticEffect for Space Sculptor")
        
        return [static_effect]

