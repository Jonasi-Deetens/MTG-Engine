# axis2/parsing/keyword_abilities/modular.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ReplacementEffect, PutCounterEffect, Subject, ParseContext, Effect, DiesEvent, TargetingRules, TargetingRestriction
from axis2.parsing.targeting import parse_targeting

logger = logging.getLogger(__name__)

MODULAR_RE = re.compile(
    r"modular\s+(\d+)",
    re.IGNORECASE
)


class ModularParser:
    """Parses Modular keyword ability (replacement effect + triggered ability)"""
    
    keyword_name = "modular"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Modular pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "+1/+1 counter" in lower and ("dies" in lower or "put into a graveyard" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Modular reminder text into ReplacementEffect and TriggeredAbility"""
        logger.debug(f"[ModularParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "+1/+1 counter" not in lower:
            return []
        
        m = MODULAR_RE.search(reminder_text)
        if not m:
            logger.debug(f"[ModularParser] No modular value found in reminder text")
            return []
        
        modular_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": modular_value},
            zones=["battlefield"]
        )
        
        condition_text = "When this permanent is put into a graveyard from the battlefield, you may put a +1/+1 counter on target artifact creature for each +1/+1 counter on this permanent."
        
        effect_text = "Put a +1/+1 counter on target artifact creature for each +1/+1 counter on this permanent."
        
        from axis2.parsing.effects.dispatcher import parse_effect_text
        effects = parse_effect_text(effect_text, ctx)
        
        targeting = parse_targeting(effect_text)
        if not targeting:
            targeting = TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["creature"],
                restrictions=[TargetingRestriction(type="types", conditions=[{"types": ["artifact"]}])]
            )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event=DiesEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[ModularParser] Created ReplacementEffect and TriggeredAbility for Modular {modular_value}")
        
        return [replacement_effect, triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Modular keyword without reminder text (e.g., 'Modular 3')"""
        logger.debug(f"[ModularParser] Parsing keyword only: {keyword_text}")
        
        m = MODULAR_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ModularParser] No modular value found in keyword text")
            return []
        
        modular_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": modular_value},
            zones=["battlefield"]
        )
        
        condition_text = "When this permanent is put into a graveyard from the battlefield, you may put a +1/+1 counter on target artifact creature for each +1/+1 counter on this permanent."
        
        effect_text = "Put a +1/+1 counter on target artifact creature for each +1/+1 counter on this permanent."
        
        from axis2.parsing.effects.dispatcher import parse_effect_text
        effects = parse_effect_text(effect_text, ctx)
        
        targeting = parse_targeting(effect_text)
        if not targeting:
            targeting = TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["creature"],
                restrictions=[TargetingRestriction(type="types", conditions=[{"types": ["artifact"]}])]
            )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event=DiesEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[ModularParser] Created ReplacementEffect and TriggeredAbility for Modular {modular_value}")
        
        return [replacement_effect, triggered_ability]

