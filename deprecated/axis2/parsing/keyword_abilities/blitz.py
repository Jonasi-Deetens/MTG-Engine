# axis2/parsing/keyword_abilities/blitz.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, TriggeredAbility, DiesEvent, ChangeZoneEffect, Subject, ParseContext, Effect, GrantedAbility

logger = logging.getLogger(__name__)

BLITZ_RE = re.compile(
    r"blitz\s+(.+)",
    re.IGNORECASE
)


class BlitzParser:
    """Parses Blitz keyword ability (spell modifier + static + triggered abilities)"""
    
    keyword_name = "blitz"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Blitz pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "blitz cost" in lower and ("haste" in lower or "dies" in lower or "draw a card" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Blitz reminder text"""
        logger.debug(f"[BlitzParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "blitz cost" not in lower:
            return []
        
        m = BLITZ_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[BlitzParser] Detected Blitz cost: {cost_text}")
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            condition="blitz_cost_was_paid",
            source_kind="static_ability"
        )
        
        draw_trigger = TriggeredAbility(
            condition_text="When this permanent is put into a graveyard from the battlefield, draw a card.",
            effects=[],  # Axis3 handles the draw
            event=DiesEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="blitz_cost_was_paid"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, sacrifice this permanent.",
            effects=[sacrifice_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None,
            condition="blitz_cost_was_paid"
        )
        
        logger.debug(f"[BlitzParser] Created ContinuousEffect and TriggeredAbilities for Blitz")
        
        return [haste_effect, draw_trigger, end_step_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Blitz keyword without reminder text (e.g., 'Blitz {1}{R}')"""
        logger.debug(f"[BlitzParser] Parsing keyword only: {keyword_text}")
        
        m = BLITZ_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[BlitzParser] Detected Blitz cost: {cost_text}")
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            condition="blitz_cost_was_paid",
            source_kind="static_ability"
        )
        
        draw_trigger = TriggeredAbility(
            condition_text="When this permanent is put into a graveyard from the battlefield, draw a card.",
            effects=[],  # Axis3 handles the draw
            event=DiesEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="blitz_cost_was_paid"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, sacrifice this permanent.",
            effects=[sacrifice_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None,
            condition="blitz_cost_was_paid"
        )
        
        logger.debug(f"[BlitzParser] Created ContinuousEffect and TriggeredAbilities for Blitz")
        
        return [haste_effect, draw_trigger, end_step_trigger]

