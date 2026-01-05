# axis2/parsing/keyword_abilities/rampage.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ContinuousEffect, PTExpression, ParseContext, Effect

logger = logging.getLogger(__name__)

RAMPAGE_RE = re.compile(
    r"rampage\s+(\d+)",
    re.IGNORECASE
)


class RampageParser:
    """Parses Rampage keyword ability (triggered ability with parameter)"""
    
    keyword_name = "rampage"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Rampage pattern"""
        lower = reminder_text.lower()
        return "becomes blocked" in lower and "gets +" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Rampage reminder text into TriggeredAbility"""
        logger.debug(f"[RampageParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "becomes blocked" not in lower or "gets +" not in lower:
            return []
        
        m = RAMPAGE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[RampageParser] No rampage value found in reminder text")
            return []
        
        rampage_value = int(m.group(1))
        
        condition_text = "Whenever this creature becomes blocked"
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(
                power=f"+{rampage_value}",
                toughness=f"+{rampage_value}"
            ),
            text=f"gets +{rampage_value}/+{rampage_value} until end of turn for each creature blocking it beyond the first",
            source_kind="triggered_ability",
            condition="blockers_beyond_first"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[pt_effect],
            event="becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[RampageParser] Created TriggeredAbility for Rampage {rampage_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Rampage keyword without reminder text (e.g., 'Rampage 2')"""
        logger.debug(f"[RampageParser] Parsing keyword only: {keyword_text}")
        
        m = RAMPAGE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[RampageParser] No rampage value found in keyword text")
            return []
        
        rampage_value = int(m.group(1))
        
        condition_text = "Whenever this creature becomes blocked"
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(
                power=f"+{rampage_value}",
                toughness=f"+{rampage_value}"
            ),
            text=f"gets +{rampage_value}/+{rampage_value} until end of turn for each creature blocking it beyond the first",
            source_kind="triggered_ability",
            condition="blockers_beyond_first"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[pt_effect],
            event="becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[RampageParser] Created TriggeredAbility for Rampage {rampage_value}")
        
        return [triggered_ability]

