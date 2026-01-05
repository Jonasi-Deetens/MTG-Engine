# axis2/parsing/keyword_abilities/unearth.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ChangeZoneEffect, ContinuousEffect, TriggeredAbility, ReplacementEffect, Subject, ParseContext, Effect, GrantedAbility
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

UNEARTH_RE = re.compile(
    r"unearth\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class UnearthParser:
    """Parses Unearth keyword ability (activated ability from graveyard)"""
    
    keyword_name = "unearth"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Unearth pattern"""
        lower = reminder_text.lower()
        return "return this card" in lower and "graveyard" in lower and "gains haste" in lower and "exile it" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Unearth reminder text into ActivatedAbility"""
        logger.debug(f"[UnearthParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "return this card" not in lower or "graveyard" not in lower:
            return []
        
        m = UNEARTH_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="battlefield",
            owner="owner"
        )
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            source_kind="activated_ability"
        )
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="exile",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, exile this permanent.",
            effects=[exile_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None
        )
        
        leave_battlefield_exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="exile",
            owner="owner"
        )
        
        replacement_effect = ReplacementEffect(
            kind="zone_change",
            event="would_leave_battlefield",
            subject=Subject(scope="self"),
            instead_effects=[leave_battlefield_exile_effect],
            zones=["battlefield"]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[return_effect, haste_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[UnearthParser] Created ActivatedAbility, TriggeredAbility, and ReplacementEffect for Unearth")
        
        return [activated_ability, end_step_trigger, replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Unearth keyword without reminder text (e.g., 'Unearth {B}')"""
        logger.debug(f"[UnearthParser] Parsing keyword only: {keyword_text}")
        
        m = UNEARTH_RE.search(keyword_text)
        if not m:
            logger.debug(f"[UnearthParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="battlefield",
            owner="owner"
        )
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            source_kind="activated_ability"
        )
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="exile",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, exile this permanent.",
            effects=[exile_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[return_effect, haste_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[UnearthParser] Created ActivatedAbility and TriggeredAbility for Unearth {cost_text}")
        
        return [activated_ability, end_step_trigger]

