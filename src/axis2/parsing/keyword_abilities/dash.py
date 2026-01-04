# axis2/parsing/keyword_abilities/dash.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ChangeZoneEffect, ContinuousEffect, Subject, ParseContext, Effect, GrantedAbility

logger = logging.getLogger(__name__)

DASH_RE = re.compile(
    r"dash\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class DashParser:
    """Parses Dash keyword ability (spell modifier + triggered ability + static ability)"""
    
    keyword_name = "dash"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Dash pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "dash cost" in lower and "haste" in lower and "return" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Dash reminder text"""
        logger.debug(f"[DashParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "dash cost" not in lower:
            return []
        
        m = DASH_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[DashParser] Detected Dash cost: {cost_text}")
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, return this permanent to its owner's hand.",
            effects=[return_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None,
            condition="dash_cost_was_paid"
        )
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            source_kind="static_ability",
            condition="dash_cost_was_paid"
        )
        
        logger.debug(f"[DashParser] Created TriggeredAbility and ContinuousEffect for Dash")
        
        return [end_step_trigger, haste_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Dash keyword without reminder text (e.g., 'Dash {2}{R}')"""
        logger.debug(f"[DashParser] Parsing keyword only: {keyword_text}")
        
        m = DASH_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[DashParser] Detected Dash cost: {cost_text}")
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, return this permanent to its owner's hand.",
            effects=[return_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None,
            condition="dash_cost_was_paid"
        )
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            source_kind="static_ability",
            condition="dash_cost_was_paid"
        )
        
        logger.debug(f"[DashParser] Created TriggeredAbility and ContinuousEffect for Dash")
        
        return [end_step_trigger, haste_effect]

