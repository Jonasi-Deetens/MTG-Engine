# axis2/parsing/keyword_abilities/dredge.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect, ChangeZoneEffect

logger = logging.getLogger(__name__)

DREDGE_RE = re.compile(
    r"dredge\s+(\d+)",
    re.IGNORECASE
)


class DredgeParser:
    """Parses Dredge keyword ability (replacement effect)"""
    
    keyword_name = "dredge"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Dredge pattern"""
        lower = reminder_text.lower()
        return "draw a card" in lower and "mill" in lower and "return this card" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Dredge reminder text into ReplacementEffect"""
        logger.debug(f"[DredgeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "draw a card" not in lower or "mill" not in lower or "return this card" not in lower:
            return []
        
        m = DREDGE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[DredgeParser] No dredge value found in reminder text")
            return []
        
        dredge_value = int(m.group(1))
        
        mill_effect = ChangeZoneEffect(
            subject=Subject(scope="each", types=["card"]),
            from_zone="library",
            to_zone="graveyard",
            owner="owner"
        )
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="hand",
            owner="owner"
        )
        
        replacement_effect = ReplacementEffect(
            kind="replace_draw",
            event="would_draw_card",
            subject=Subject(scope="self"),
            instead_effects=[mill_effect, return_effect],
            condition=f"library_has_at_least_{dredge_value}_cards"
        )
        
        logger.debug(f"[DredgeParser] Created ReplacementEffect for Dredge {dredge_value}")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Dredge keyword without reminder text (e.g., 'Dredge 3')"""
        logger.debug(f"[DredgeParser] Parsing keyword only: {keyword_text}")
        
        m = DREDGE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[DredgeParser] No dredge value found in keyword text")
            return []
        
        dredge_value = int(m.group(1))
        
        mill_effect = ChangeZoneEffect(
            subject=Subject(scope="each", types=["card"]),
            from_zone="library",
            to_zone="graveyard",
            owner="owner"
        )
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="hand",
            owner="owner"
        )
        
        replacement_effect = ReplacementEffect(
            kind="replace_draw",
            event="would_draw_card",
            subject=Subject(scope="self"),
            instead_effects=[mill_effect, return_effect],
            condition=f"library_has_at_least_{dredge_value}_cards"
        )
        
        logger.debug(f"[DredgeParser] Created ReplacementEffect for Dredge {dredge_value}")
        
        return [replacement_effect]

