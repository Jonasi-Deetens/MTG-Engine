# axis2/parsing/keyword_abilities/bushido.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ContinuousEffect, PTExpression, ParseContext, Effect

logger = logging.getLogger(__name__)

BUSHIDO_RE = re.compile(
    r"bushido\s+(\d+)",
    re.IGNORECASE
)


class BushidoParser:
    """Parses Bushido keyword ability (triggered ability)"""
    
    keyword_name = "bushido"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Bushido pattern"""
        lower = reminder_text.lower()
        return ("blocks" in lower or "becomes blocked" in lower) and "gets +" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bushido reminder text into TriggeredAbility"""
        logger.debug(f"[BushidoParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if ("blocks" not in lower and "becomes blocked" not in lower) or "gets +" not in lower:
            return []
        
        m = BUSHIDO_RE.search(reminder_text)
        if not m:
            logger.debug(f"[BushidoParser] No bushido value found in reminder text")
            return []
        
        bushido_value = int(m.group(1))
        
        condition_text = "Whenever this creature blocks or becomes blocked"
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(
                power=f"+{bushido_value}",
                toughness=f"+{bushido_value}"
            ),
            text=f"gets +{bushido_value}/+{bushido_value} until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[pt_effect],
            event="blocks_or_becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[BushidoParser] Created TriggeredAbility for Bushido {bushido_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bushido keyword without reminder text (e.g., 'Bushido 1')"""
        logger.debug(f"[BushidoParser] Parsing keyword only: {keyword_text}")
        
        m = BUSHIDO_RE.search(keyword_text)
        if not m:
            logger.debug(f"[BushidoParser] No bushido value found in keyword text")
            return []
        
        bushido_value = int(m.group(1))
        
        condition_text = "Whenever this creature blocks or becomes blocked"
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(
                power=f"+{bushido_value}",
                toughness=f"+{bushido_value}"
            ),
            text=f"gets +{bushido_value}/+{bushido_value} until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[pt_effect],
            event="blocks_or_becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[BushidoParser] Created TriggeredAbility for Bushido {bushido_value}")
        
        return [triggered_ability]

