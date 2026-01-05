# axis2/parsing/keyword_abilities/ripple.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CastSpellEvent, Subject, ParseContext, Effect, LookAndPickEffect, SpellFilter

logger = logging.getLogger(__name__)

RIPPLE_RE = re.compile(
    r"ripple\s+(\d+)",
    re.IGNORECASE
)


class RippleParser:
    """Parses Ripple keyword ability (triggered ability on stack)"""
    
    keyword_name = "ripple"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Ripple pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "reveal" in lower and "same name" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ripple reminder text into TriggeredAbility"""
        logger.debug(f"[RippleParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "reveal" not in lower:
            return []
        
        m = RIPPLE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[RippleParser] No ripple value found in reminder text")
            return []
        
        ripple_value = int(m.group(1))
        
        look_and_pick_effect = LookAndPickEffect(
            look_at=ripple_value,
            source_zone="library",
            reveal_up_to=ripple_value,
            reveal_types=None,
            put_revealed_into="stack",
            put_rest_into="bottom",
            rest_order="any",
            optional=True
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When you cast this spell, you may reveal the top {ripple_value} cards of your library. You may cast any revealed cards with the same name as this spell without paying their mana costs. Put the rest on the bottom of your library.",
            effects=[look_and_pick_effect],
            event=CastSpellEvent(subject="this_spell", spell_filter=SpellFilter()),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[RippleParser] Created TriggeredAbility for Ripple {ripple_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ripple keyword without reminder text (e.g., 'Ripple 4')"""
        logger.debug(f"[RippleParser] Parsing keyword only: {keyword_text}")
        
        m = RIPPLE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[RippleParser] No ripple value found in keyword text")
            return []
        
        ripple_value = int(m.group(1))
        
        look_and_pick_effect = LookAndPickEffect(
            look_at=ripple_value,
            source_zone="library",
            reveal_up_to=ripple_value,
            reveal_types=None,
            put_revealed_into="stack",
            put_rest_into="bottom",
            rest_order="any",
            optional=True
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When you cast this spell, you may reveal the top {ripple_value} cards of your library. You may cast any revealed cards with the same name as this spell without paying their mana costs. Put the rest on the bottom of your library.",
            effects=[look_and_pick_effect],
            event=CastSpellEvent(subject="this_spell", spell_filter=SpellFilter()),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[RippleParser] Created TriggeredAbility for Ripple {ripple_value}")
        
        return [triggered_ability]

