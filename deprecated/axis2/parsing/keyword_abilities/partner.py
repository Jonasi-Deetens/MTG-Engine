# axis2/parsing/keyword_abilities/partner.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, SearchEffect, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

PARTNER_WITH_RE = re.compile(
    r"partner\s+with\s+(.+)",
    re.IGNORECASE
)


class PartnerParser:
    """Parses Partner keyword ability (deck construction + optional triggered ability)"""
    
    keyword_name = "partner"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Partner pattern"""
        lower = reminder_text.lower()
        return "two commanders" in lower or "enters" in lower and "search" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Partner reminder text"""
        logger.debug(f"[PartnerParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        
        m = PARTNER_WITH_RE.search(reminder_text)
        if m:
            partner_name = m.group(1).strip()
            logger.debug(f"[PartnerParser] Detected Partner with: {partner_name}")
            
            if "enters" in lower and "search" in lower:
                search_effect = SearchEffect(
                    zones=["library"],
                    card_names=[partner_name],
                    optional=True,
                    put_onto_battlefield=False,
                    shuffle_if_library_searched=True,
                    card_filter=None,
                    max_results=1
                )
                
                put_into_hand_effect = ChangeZoneEffect(
                    subject=Subject(scope="searched_card"),
                    from_zone="library",
                    to_zone="hand",
                    owner="owner"
                )
                
                triggered_ability = TriggeredAbility(
                    condition_text=f"When this permanent enters the battlefield, target player may search their library for a card named {partner_name}, reveal it, put it into their hand, then shuffle.",
                    effects=[search_effect, put_into_hand_effect],
                    event=EntersBattlefieldEvent(subject="self"),
                    targeting=None,
                    trigger_filter=None
                )
                
                logger.debug(f"[PartnerParser] Created TriggeredAbility for Partner with {partner_name}")
                return [triggered_ability]
        
        logger.debug(f"[PartnerParser] Detected Partner (deck construction only)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Partner keyword without reminder text"""
        logger.debug(f"[PartnerParser] Parsing keyword only: {keyword_text}")
        
        m = PARTNER_WITH_RE.search(keyword_text)
        if m:
            partner_name = m.group(1).strip()
            logger.debug(f"[PartnerParser] Detected Partner with: {partner_name}")
        
        logger.debug(f"[PartnerParser] Detected Partner (deck construction only)")
        
        return []

