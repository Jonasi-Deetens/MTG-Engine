# axis2/parsing/keyword_abilities/morph.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

MORPH_RE = re.compile(
    r"(?:mega|morph|negamorph)\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class MorphParser:
    """Parses Morph keyword ability (spell modifier with cost)"""
    
    keyword_name = "morph"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Morph pattern"""
        lower = reminder_text.lower()
        return "cast this face down" in lower or "cast this card face down" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Morph reminder text"""
        logger.debug(f"[MorphParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this face down" not in lower and "cast this card face down" not in lower:
            return []
        
        m = MORPH_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MorphParser] Detected Morph with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Morph keyword without reminder text (e.g., 'Morph {U}')"""
        logger.debug(f"[MorphParser] Parsing keyword only: {keyword_text}")
        
        m = MORPH_RE.search(keyword_text)
        if not m:
            logger.debug(f"[MorphParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MorphParser] Detected Morph with cost: {cost_text}")
        
        return []


class MegamorphParser:
    """Parses Megamorph keyword ability (spell modifier with cost)"""
    
    keyword_name = "megamorph"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Megamorph pattern"""
        lower = reminder_text.lower()
        return "cast this face down" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Megamorph reminder text"""
        logger.debug(f"[MegamorphParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this face down" not in lower or "+1/+1 counter" not in lower:
            return []
        
        m = MORPH_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MegamorphParser] Detected Megamorph with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Megamorph keyword without reminder text (e.g., 'Megamorph {5}{W}{W}')"""
        logger.debug(f"[MegamorphParser] Parsing keyword only: {keyword_text}")
        
        m = MORPH_RE.search(keyword_text)
        if not m:
            logger.debug(f"[MegamorphParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MegamorphParser] Detected Megamorph with cost: {cost_text}")
        
        return []

