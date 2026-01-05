# axis2/parsing/keyword_abilities/toxic.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, RuleChangeData, ParseContext, Effect

logger = logging.getLogger(__name__)

TOXIC_RE = re.compile(
    r"toxic\s+(\d+)",
    re.IGNORECASE
)


class ToxicParser:
    """Parses Toxic keyword ability (static ability)"""
    
    keyword_name = "toxic"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Toxic pattern"""
        lower = reminder_text.lower()
        return "combat damage" in lower and "poison counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Toxic reminder text into ContinuousEffect"""
        logger.debug(f"[ToxicParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "combat damage" not in lower or "poison counter" not in lower:
            return []
        
        m = TOXIC_RE.search(reminder_text)
        if not m:
            logger.debug(f"[ToxicParser] No toxic value found in reminder text")
            return []
        
        toxic_value = int(m.group(1))
        
        continuous_effect = ContinuousEffect(
            kind="rule_change",
            text=f"Combat damage dealt to a player by this creature also causes that player to get {toxic_value} poison counter{'s' if toxic_value != 1 else ''}.",
            applies_to="damage_dealt_by_self",
            duration="permanent",
            layer=6,
            rule_change=RuleChangeData(kind=f"toxic_{toxic_value}"),
            source_kind="static_ability"
        )
        
        logger.debug(f"[ToxicParser] Created ContinuousEffect for Toxic {toxic_value}")
        
        return [continuous_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Toxic keyword without reminder text (e.g., 'Toxic 1')"""
        logger.debug(f"[ToxicParser] Parsing keyword only: {keyword_text}")
        
        m = TOXIC_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ToxicParser] No toxic value found in keyword text")
            return []
        
        toxic_value = int(m.group(1))
        
        continuous_effect = ContinuousEffect(
            kind="rule_change",
            text=f"Combat damage dealt to a player by this creature also causes that player to get {toxic_value} poison counter{'s' if toxic_value != 1 else ''}.",
            applies_to="damage_dealt_by_self",
            duration="permanent",
            layer=6,
            rule_change=RuleChangeData(kind=f"toxic_{toxic_value}"),
            source_kind="static_ability"
        )
        
        logger.debug(f"[ToxicParser] Created ContinuousEffect for Toxic {toxic_value}")
        
        return [continuous_effect]

