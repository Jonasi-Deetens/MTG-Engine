# axis2/parsing/keyword_abilities/miracle.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

MIRACLE_RE = re.compile(
    r"miracle\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class MiracleParser:
    """Parses Miracle keyword ability (static ability linked to triggered ability)"""
    
    keyword_name = "miracle"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Miracle pattern"""
        lower = reminder_text.lower()
        return "cast this card" in lower and "draw it" in lower and "first card" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Miracle reminder text into TriggeredAbility"""
        logger.debug(f"[MiracleParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card" not in lower or "draw it" not in lower:
            return []
        
        m = MIRACLE_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        triggered_ability = TriggeredAbility(
            condition_text=f"You may reveal this card from your hand as you draw it if it's the first card you've drawn this turn. When you reveal this card this way, you may cast it by paying {cost_text} rather than its mana cost.",
            effects=[],  # The casting happens as part of the trigger resolution
            event="draw_card",
            targeting=None,
            trigger_filter=None,
            condition="first_card_drawn_this_turn"
        )
        
        logger.debug(f"[MiracleParser] Created TriggeredAbility for Miracle")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Miracle keyword without reminder text (e.g., 'Miracle {W}')"""
        logger.debug(f"[MiracleParser] Parsing keyword only: {keyword_text}")
        
        m = MIRACLE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[MiracleParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        triggered_ability = TriggeredAbility(
            condition_text=f"You may reveal this card from your hand as you draw it if it's the first card you've drawn this turn. When you reveal this card this way, you may cast it by paying {cost_text} rather than its mana cost.",
            effects=[],  # The casting happens as part of the trigger resolution
            event="draw_card",
            targeting=None,
            trigger_filter=None,
            condition="first_card_drawn_this_turn"
        )
        
        logger.debug(f"[MiracleParser] Created TriggeredAbility for Miracle {cost_text}")
        
        return [triggered_ability]

