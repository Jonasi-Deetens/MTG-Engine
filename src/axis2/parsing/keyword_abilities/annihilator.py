# axis2/parsing/keyword_abilities/annihilator.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, ChangeZoneEffect, Subject, ParseContext, Effect, TargetingRules

logger = logging.getLogger(__name__)

ANNIHILATOR_RE = re.compile(
    r"annihilator\s+(\d+)",
    re.IGNORECASE
)


class AnnihilatorParser:
    """Parses Annihilator keyword ability (triggered ability)"""
    
    keyword_name = "annihilator"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Annihilator pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "defending player sacrifices" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Annihilator reminder text into TriggeredAbility"""
        logger.debug(f"[AnnihilatorParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "defending player sacrifices" not in lower:
            return []
        
        m = ANNIHILATOR_RE.search(reminder_text)
        if not m:
            logger.debug(f"[AnnihilatorParser] No annihilator value found in reminder text")
            return []
        
        annihilator_value = int(m.group(1))
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="any_number", max_targets=annihilator_value, types=["permanent"], controller="defending_player"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="controller"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature attacks, defending player sacrifices {annihilator_value} permanents.",
            effects=[sacrifice_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[AnnihilatorParser] Created TriggeredAbility for Annihilator {annihilator_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Annihilator keyword without reminder text (e.g., 'Annihilator 2')"""
        logger.debug(f"[AnnihilatorParser] Parsing keyword only: {keyword_text}")
        
        m = ANNIHILATOR_RE.search(keyword_text)
        if not m:
            logger.debug(f"[AnnihilatorParser] No annihilator value found in keyword text")
            return []
        
        annihilator_value = int(m.group(1))
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="any_number", max_targets=annihilator_value, types=["permanent"], controller="defending_player"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="controller"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature attacks, defending player sacrifices {annihilator_value} permanents.",
            effects=[sacrifice_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[AnnihilatorParser] Created TriggeredAbility for Annihilator {annihilator_value}")
        
        return [triggered_ability]

