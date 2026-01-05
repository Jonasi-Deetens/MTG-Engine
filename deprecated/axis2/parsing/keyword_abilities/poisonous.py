# axis2/parsing/keyword_abilities/poisonous.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DealsDamageEvent, PutCounterEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

POISONOUS_RE = re.compile(
    r"poisonous\s+(\d+)",
    re.IGNORECASE
)


class PoisonousParser:
    """Parses Poisonous keyword ability (triggered ability)"""
    
    keyword_name = "poisonous"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Poisonous pattern"""
        lower = reminder_text.lower()
        return "deals combat damage" in lower and "player" in lower and "poison counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Poisonous reminder text into TriggeredAbility"""
        logger.debug(f"[PoisonousParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "deals combat damage" not in lower or "player" not in lower or "poison counter" not in lower:
            return []
        
        m = POISONOUS_RE.search(reminder_text)
        if not m:
            logger.debug(f"[PoisonousParser] No poisonous value found in reminder text")
            return []
        
        poisonous_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="poison",
            amount=poisonous_value
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature deals combat damage to a player, that player gets {poisonous_value} poison counter{'s' if poisonous_value != 1 else ''}.",
            effects=[put_counter_effect],
            event=DealsDamageEvent(subject="self", target="player", damage_type="combat"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[PoisonousParser] Created TriggeredAbility for Poisonous {poisonous_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Poisonous keyword without reminder text (e.g., 'Poisonous 1')"""
        logger.debug(f"[PoisonousParser] Parsing keyword only: {keyword_text}")
        
        m = POISONOUS_RE.search(keyword_text)
        if not m:
            logger.debug(f"[PoisonousParser] No poisonous value found in keyword text")
            return []
        
        poisonous_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="poison",
            amount=poisonous_value
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature deals combat damage to a player, that player gets {poisonous_value} poison counter{'s' if poisonous_value != 1 else ''}.",
            effects=[put_counter_effect],
            event=DealsDamageEvent(subject="self", target="player", damage_type="combat"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[PoisonousParser] Created TriggeredAbility for Poisonous {poisonous_value}")
        
        return [triggered_ability]

