# axis2/parsing/keyword_abilities/frenzy.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, ContinuousEffect, PTExpression, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

FRENZY_RE = re.compile(
    r"frenzy\s+(\d+)",
    re.IGNORECASE
)


class FrenzyParser:
    """Parses Frenzy keyword ability (triggered ability)"""
    
    keyword_name = "frenzy"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Frenzy pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "isn't blocked" in lower and "gets +" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Frenzy reminder text into TriggeredAbility"""
        logger.debug(f"[FrenzyParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "isn't blocked" not in lower or "gets +" not in lower:
            return []
        
        m = FRENZY_RE.search(reminder_text)
        if not m:
            logger.debug(f"[FrenzyParser] No frenzy value found in reminder text")
            return []
        
        frenzy_value = int(m.group(1))
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power=f"+{frenzy_value}", toughness="+0"),
            text=f"gets +{frenzy_value}/+0 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature attacks and isn't blocked, it gets +{frenzy_value}/+0 until end of turn.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FrenzyParser] Created TriggeredAbility for Frenzy {frenzy_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Frenzy keyword without reminder text (e.g., 'Frenzy 1')"""
        logger.debug(f"[FrenzyParser] Parsing keyword only: {keyword_text}")
        
        m = FRENZY_RE.search(keyword_text)
        if not m:
            logger.debug(f"[FrenzyParser] No frenzy value found in keyword text")
            return []
        
        frenzy_value = int(m.group(1))
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power=f"+{frenzy_value}", toughness="+0"),
            text=f"gets +{frenzy_value}/+0 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature attacks and isn't blocked, it gets +{frenzy_value}/+0 until end of turn.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FrenzyParser] Created TriggeredAbility for Frenzy {frenzy_value}")
        
        return [triggered_ability]

