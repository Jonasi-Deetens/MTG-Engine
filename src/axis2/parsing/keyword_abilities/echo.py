# axis2/parsing/keyword_abilities/echo.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

ECHO_COST_RE = re.compile(
    r"echo\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class EchoParser:
    """Parses Echo keyword ability (triggered ability with cost)"""
    
    keyword_name = "echo"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Echo pattern"""
        lower = reminder_text.lower()
        return "beginning of your upkeep" in lower and "sacrifice it unless" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Echo reminder text into TriggeredAbility"""
        logger.debug(f"[EchoParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "beginning of your upkeep" not in lower or "sacrifice it unless" not in lower:
            return []
        
        m = ECHO_COST_RE.search(reminder_text)
        cost_text = None
        if m:
            cost_text = m.group(1).strip()
        
        condition_text = "At the beginning of your upkeep, if this permanent came under your control since the beginning of your last upkeep"
        
        from axis2.schema import ChangeZoneEffect, Subject
        effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[EchoParser] Created TriggeredAbility for Echo")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Echo keyword without reminder text (e.g., 'Echo {2}{R}')"""
        logger.debug(f"[EchoParser] Parsing keyword only: {keyword_text}")
        
        m = ECHO_COST_RE.search(keyword_text)
        if not m:
            logger.debug(f"[EchoParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        condition_text = "At the beginning of your upkeep, if this permanent came under your control since the beginning of your last upkeep"
        
        from axis2.schema import ChangeZoneEffect, Subject
        effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[EchoParser] Created TriggeredAbility for Echo {cost_text}")
        
        return [triggered_ability]

