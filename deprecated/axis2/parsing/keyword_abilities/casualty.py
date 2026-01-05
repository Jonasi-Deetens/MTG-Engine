# axis2/parsing/keyword_abilities/casualty.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CastSpellEvent, ParseContext, Effect

logger = logging.getLogger(__name__)

CASUALTY_RE = re.compile(
    r"casualty\s+(\d+)",
    re.IGNORECASE
)


class CasualtyParser:
    """Parses Casualty keyword ability (spell modifier)"""
    
    keyword_name = "casualty"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Casualty pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "sacrifice a creature" in lower and "power" in lower and "copy" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Casualty reminder text"""
        logger.debug(f"[CasualtyParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "sacrifice a creature" not in lower or "copy" not in lower:
            return []
        
        m = CASUALTY_RE.search(reminder_text)
        if not m:
            logger.debug(f"[CasualtyParser] No casualty value found in reminder text")
            return []
        
        casualty_value = int(m.group(1))
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When you cast this spell, if a casualty cost was paid for it, copy it. If the spell has any targets, you may choose new targets for the copy.",
            effects=[],  # Axis3 handles the copying
            event=CastSpellEvent(subject="this_spell"),
            targeting=None,
            trigger_filter=None,
            condition=f"casualty_{casualty_value}_cost_was_paid"
        )
        
        logger.debug(f"[CasualtyParser] Created TriggeredAbility for Casualty {casualty_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Casualty keyword without reminder text (e.g., 'Casualty 1')"""
        logger.debug(f"[CasualtyParser] Parsing keyword only: {keyword_text}")
        
        m = CASUALTY_RE.search(keyword_text)
        if not m:
            logger.debug(f"[CasualtyParser] No casualty value found in keyword text")
            return []
        
        casualty_value = int(m.group(1))
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When you cast this spell, if a casualty cost was paid for it, copy it. If the spell has any targets, you may choose new targets for the copy.",
            effects=[],
            event=CastSpellEvent(subject="this_spell"),
            targeting=None,
            trigger_filter=None,
            condition=f"casualty_{casualty_value}_cost_was_paid"
        )
        
        logger.debug(f"[CasualtyParser] Created TriggeredAbility for Casualty {casualty_value}")
        
        return [triggered_ability]

