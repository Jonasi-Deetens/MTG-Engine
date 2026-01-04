# axis2/parsing/keyword_abilities/absorb.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

ABSORB_RE = re.compile(
    r"absorb\s+(\d+)",
    re.IGNORECASE
)


class AbsorbParser:
    """Parses Absorb keyword ability (static ability)"""
    
    keyword_name = "absorb"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Absorb pattern"""
        lower = reminder_text.lower()
        return "source would deal damage" in lower and "prevent" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Absorb reminder text into ContinuousEffect"""
        logger.debug(f"[AbsorbParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "source would deal damage" not in lower or "prevent" not in lower:
            return []
        
        m = ABSORB_RE.search(reminder_text)
        if not m:
            logger.debug(f"[AbsorbParser] No absorb value found in reminder text")
            return []
        
        absorb_value = int(m.group(1))
        
        continuous_effect = ContinuousEffect(
            kind="damage_prevention",
            applies_to="self",
            duration="permanent",
            layer=6,
            value={"prevent_amount": absorb_value},
            source_kind="static_ability"
        )
        
        logger.debug(f"[AbsorbParser] Created ContinuousEffect for Absorb {absorb_value}")
        
        return [continuous_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Absorb keyword without reminder text (e.g., 'Absorb 1')"""
        logger.debug(f"[AbsorbParser] Parsing keyword only: {keyword_text}")
        
        m = ABSORB_RE.search(keyword_text)
        if not m:
            logger.debug(f"[AbsorbParser] No absorb value found in keyword text")
            return []
        
        absorb_value = int(m.group(1))
        
        continuous_effect = ContinuousEffect(
            kind="damage_prevention",
            applies_to="self",
            duration="permanent",
            layer=6,
            value={"prevent_amount": absorb_value},
            source_kind="static_ability"
        )
        
        logger.debug(f"[AbsorbParser] Created ContinuousEffect for Absorb {absorb_value}")
        
        return [continuous_effect]

