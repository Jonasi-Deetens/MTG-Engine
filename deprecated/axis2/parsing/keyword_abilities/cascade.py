# axis2/parsing/keyword_abilities/cascade.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CastSpellEvent, Subject, ParseContext, Effect, SpellFilter, LookAndPickEffect

logger = logging.getLogger(__name__)


class CascadeParser:
    """Parses Cascade keyword ability (triggered ability on stack)"""
    
    keyword_name = "cascade"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Cascade pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "exile cards" in lower and "top of your library" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cascade reminder text into TriggeredAbility"""
        logger.debug(f"[CascadeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "exile cards" not in lower:
            return []
        
        look_and_pick_effect = LookAndPickEffect(
            look_at=999,  # Exile until we find a nonland card
            source_zone="library",
            reveal_up_to=1,
            reveal_types=None,
            put_revealed_into="stack",  # Cast the card
            put_rest_into="bottom",
            rest_order="random",
            optional=False
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When you cast this spell, exile cards from the top of your library until you exile a nonland card whose mana value is less than this spell's mana value. You may cast that card without paying its mana cost if the resulting spell's mana value is less than this spell's mana value. Then put all cards exiled this way that weren't cast on the bottom of your library in a random order.",
            effects=[look_and_pick_effect],
            event=CastSpellEvent(subject="this_spell", spell_filter=SpellFilter()),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[CascadeParser] Created TriggeredAbility for Cascade")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cascade keyword without reminder text"""
        logger.debug(f"[CascadeParser] Parsing keyword only: {keyword_text}")
        
        look_and_pick_effect = LookAndPickEffect(
            look_at=999,  # Exile until we find a nonland card
            source_zone="library",
            reveal_up_to=1,
            reveal_types=None,
            put_revealed_into="stack",  # Cast the card
            put_rest_into="bottom",
            rest_order="random",
            optional=False
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When you cast this spell, exile cards from the top of your library until you exile a nonland card whose mana value is less than this spell's mana value. You may cast that card without paying its mana cost if the resulting spell's mana value is less than this spell's mana value. Then put all cards exiled this way that weren't cast on the bottom of your library in a random order.",
            effects=[look_and_pick_effect],
            event=CastSpellEvent(subject="this_spell", spell_filter=SpellFilter()),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[CascadeParser] Created TriggeredAbility for Cascade")
        
        return [triggered_ability]

