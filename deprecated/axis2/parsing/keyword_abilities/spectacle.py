# axis2/parsing/keyword_abilities/spectacle.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

SPECTACLE_RE = re.compile(
    r"spectacle\s+(.+)",
    re.IGNORECASE
)


class SpectacleParser:
    """Parses Spectacle keyword ability (spell modifier)"""
    
    keyword_name = "spectacle"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Spectacle pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "spectacle cost" in lower and "opponent lost life" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Spectacle reminder text"""
        logger.debug(f"[SpectacleParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "spectacle cost" not in lower:
            return []
        
        m = SPECTACLE_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[SpectacleParser] Detected Spectacle cost: {cost_text}")
        
        logger.debug(f"[SpectacleParser] Detected Spectacle")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Spectacle keyword without reminder text (e.g., 'Spectacle {R}')"""
        logger.debug(f"[SpectacleParser] Parsing keyword only: {keyword_text}")
        
        m = SPECTACLE_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[SpectacleParser] Detected Spectacle cost: {cost_text}")
        
        logger.debug(f"[SpectacleParser] Detected Spectacle")
        
        return []

