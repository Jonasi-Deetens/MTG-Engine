# axis2/parsing/keyword_abilities/plot.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

PLOT_RE = re.compile(
    r"plot\s+(\{.+?\})",
    re.IGNORECASE
)


class PlotParser:
    """Parses Plot keyword ability (special action)"""
    
    keyword_name = "plot"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Plot pattern"""
        lower = reminder_text.lower()
        return "exile this card" in lower and "hand" in lower and "cast it" in lower and ("later turn" in lower or "future turn" in lower) and "without paying its mana cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Plot reminder text"""
        logger.debug(f"[PlotParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile this card" not in lower or "cast it" not in lower:
            return []
        
        m = PLOT_RE.search(reminder_text)
        if not m:
            logger.debug(f"[PlotParser] No plot cost found in reminder text")
            return []
        
        plot_cost = m.group(1).strip()
        
        logger.debug(f"[PlotParser] Detected Plot (special action, handled by Axis3)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Plot keyword without reminder text (e.g., 'Plot {2}{R}')"""
        logger.debug(f"[PlotParser] Parsing keyword only: {keyword_text}")
        
        m = PLOT_RE.search(keyword_text)
        if not m:
            logger.debug(f"[PlotParser] No plot cost found in keyword text")
            return []
        
        plot_cost = m.group(1).strip()
        
        logger.debug(f"[PlotParser] Detected Plot (special action, handled by Axis3)")
        
        return []

