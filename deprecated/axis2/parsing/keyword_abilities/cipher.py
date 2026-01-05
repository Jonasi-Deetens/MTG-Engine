# axis2/parsing/keyword_abilities/cipher.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DealsDamageEvent, ChangeZoneEffect, Subject, ParseContext, Effect, ContinuousEffect

logger = logging.getLogger(__name__)


class CipherParser:
    """Parses Cipher keyword ability (spell ability + static ability)"""
    
    keyword_name = "cipher"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Cipher pattern"""
        lower = reminder_text.lower()
        return "exile this spell" in lower and "encoded" in lower and "deals combat damage" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cipher reminder text into ChangeZoneEffect and TriggeredAbility"""
        logger.debug(f"[CipherParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile this spell" not in lower or "encoded" not in lower:
            return []
        
        encode_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="stack",
            to_zone="exile",
            owner="owner"
        )
        
        copy_and_cast_effect = ChangeZoneEffect(
            subject=Subject(scope="encoded_card"),
            from_zone="exile",
            to_zone="stack",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature deals combat damage to a player, you may copy the encoded card and you may cast the copy without paying its mana cost.",
            effects=[copy_and_cast_effect],
            event=DealsDamageEvent(subject="self", damage_type="combat", target="player"),
            targeting=None,
            trigger_filter=None
        )
        
        continuous_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="encoded_creature",
            duration="as_long_as_encoded",
            layer=6,
            value={"granted_ability": triggered_ability},
            source_kind="static_ability"
        )
        
        logger.debug(f"[CipherParser] Created ChangeZoneEffect and ContinuousEffect for Cipher")
        
        return [encode_effect, continuous_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cipher keyword without reminder text"""
        logger.debug(f"[CipherParser] Parsing keyword only: {keyword_text}")
        
        encode_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="stack",
            to_zone="exile",
            owner="owner"
        )
        
        copy_and_cast_effect = ChangeZoneEffect(
            subject=Subject(scope="encoded_card"),
            from_zone="exile",
            to_zone="stack",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature deals combat damage to a player, you may copy the encoded card and you may cast the copy without paying its mana cost.",
            effects=[copy_and_cast_effect],
            event=DealsDamageEvent(subject="self", damage_type="combat", target="player"),
            targeting=None,
            trigger_filter=None
        )
        
        continuous_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="encoded_creature",
            duration="as_long_as_encoded",
            layer=6,
            value={"granted_ability": triggered_ability},
            source_kind="static_ability"
        )
        
        logger.debug(f"[CipherParser] Created ChangeZoneEffect and ContinuousEffect for Cipher")
        
        return [encode_effect, continuous_effect]

