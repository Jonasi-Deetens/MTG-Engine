# axis2/parsing/keyword_abilities/soulshift.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DiesEvent, ChangeZoneEffect, Subject, ParseContext, Effect, TargetingRules, TargetingRestriction
from axis2.parsing.targeting import parse_targeting

logger = logging.getLogger(__name__)

SOULSHIFT_RE = re.compile(
    r"soulshift\s+(\d+|X)",
    re.IGNORECASE
)


class SoulshiftParser:
    """Parses Soulshift keyword ability (triggered ability)"""
    
    keyword_name = "soulshift"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Soulshift pattern"""
        lower = reminder_text.lower()
        return "dies" in lower and "return target spirit" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Soulshift reminder text into TriggeredAbility"""
        logger.debug(f"[SoulshiftParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "dies" not in lower or "return target spirit" not in lower:
            return []
        
        m = SOULSHIFT_RE.search(reminder_text)
        if not m:
            logger.debug(f"[SoulshiftParser] No soulshift value found in reminder text")
            return []
        
        soulshift_value = m.group(1)
        
        condition_text = f"When this permanent is put into a graveyard from the battlefield, you may return target Spirit card with mana value {soulshift_value} or less from your graveyard to your hand."
        
        effect_text = f"Return target Spirit card with mana value {soulshift_value} or less from your graveyard to your hand."
        
        from axis2.parsing.effects.dispatcher import parse_effect_text
        effects = parse_effect_text(effect_text, ctx)
        
        targeting = parse_targeting(effect_text)
        if not targeting:
            targeting = TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["card"],
                restrictions=[
                    TargetingRestriction(type="types", conditions=[{"types": ["creature"], "subtypes": ["spirit"]}]),
                    TargetingRestriction(type="zone", conditions=[{"zone": "graveyard"}]),
                    TargetingRestriction(type="mana_value", conditions=[{"max": soulshift_value if soulshift_value != "X" else None}])
                ]
            )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event=DiesEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[SoulshiftParser] Created TriggeredAbility for Soulshift {soulshift_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Soulshift keyword without reminder text (e.g., 'Soulshift 7')"""
        logger.debug(f"[SoulshiftParser] Parsing keyword only: {keyword_text}")
        
        m = SOULSHIFT_RE.search(keyword_text)
        if not m:
            logger.debug(f"[SoulshiftParser] No soulshift value found in keyword text")
            return []
        
        soulshift_value = m.group(1)
        
        condition_text = f"When this permanent is put into a graveyard from the battlefield, you may return target Spirit card with mana value {soulshift_value} or less from your graveyard to your hand."
        
        effect_text = f"Return target Spirit card with mana value {soulshift_value} or less from your graveyard to your hand."
        
        from axis2.parsing.effects.dispatcher import parse_effect_text
        effects = parse_effect_text(effect_text, ctx)
        
        targeting = parse_targeting(effect_text)
        if not targeting:
            targeting = TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["card"],
                restrictions=[
                    TargetingRestriction(type="types", conditions=[{"types": ["creature"], "subtypes": ["spirit"]}]),
                    TargetingRestriction(type="zone", conditions=[{"zone": "graveyard"}]),
                    TargetingRestriction(type="mana_value", conditions=[{"max": soulshift_value if soulshift_value != "X" else None}])
                ]
            )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event=DiesEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[SoulshiftParser] Created TriggeredAbility for Soulshift {soulshift_value}")
        
        return [triggered_ability]

