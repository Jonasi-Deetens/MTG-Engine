# axis2/parsing/keyword_abilities/recover.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DiesEvent, ChangeZoneEffect, Subject, ParseContext, Effect, ConditionalEffect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

RECOVER_RE = re.compile(
    r"recover\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class RecoverParser:
    """Parses Recover keyword ability (triggered ability from graveyard)"""
    
    keyword_name = "recover"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Recover pattern"""
        lower = reminder_text.lower()
        return "creature is put into your graveyard" in lower and "pay" in lower and ("return this card" in lower or "exile this card" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Recover reminder text into TriggeredAbility"""
        logger.debug(f"[RecoverParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "creature is put into your graveyard" not in lower or "pay" not in lower:
            return []
        
        m = RECOVER_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="hand",
            owner="owner"
        )
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        conditional_effect = ConditionalEffect(
            condition="if_you_pay_cost",
            effects=[return_effect]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When a creature is put into your graveyard from the battlefield, you may pay {cost_text}. If you do, return this card from your graveyard to your hand. Otherwise, exile this card.",
            effects=[conditional_effect, exile_effect],
            event=DiesEvent(subject="creature"),
            targeting=None,
            trigger_filter=None,
            cost_text=cost_text
        )
        
        logger.debug(f"[RecoverParser] Created TriggeredAbility for Recover")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Recover keyword without reminder text (e.g., 'Recover {2}{B}')"""
        logger.debug(f"[RecoverParser] Parsing keyword only: {keyword_text}")
        
        m = RECOVER_RE.search(keyword_text)
        if not m:
            logger.debug(f"[RecoverParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="hand",
            owner="owner"
        )
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        conditional_effect = ConditionalEffect(
            condition="if_you_pay_cost",
            effects=[return_effect]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When a creature is put into your graveyard from the battlefield, you may pay {cost_text}. If you do, return this card from your graveyard to your hand. Otherwise, exile this card.",
            effects=[conditional_effect, exile_effect],
            event=DiesEvent(subject="creature"),
            targeting=None,
            trigger_filter=None,
            cost_text=cost_text
        )
        
        logger.debug(f"[RecoverParser] Created TriggeredAbility for Recover {cost_text}")
        
        return [triggered_ability]

