# axis2/parsing/keyword_abilities/champion.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, LeavesBattlefieldEvent, ChangeZoneEffect, Subject, ParseContext, Effect, ConditionalEffect

logger = logging.getLogger(__name__)

CHAMPION_RE = re.compile(
    r"champion\s+(?:an?\s+)?(.+)",
    re.IGNORECASE
)


class ChampionParser:
    """Parses Champion keyword ability (two linked triggered abilities)"""
    
    keyword_name = "champion"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Champion pattern"""
        lower = reminder_text.lower()
        return "enters the battlefield" in lower and "exile" in lower and "leaves the battlefield" in lower and "returns" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Champion reminder text into two TriggeredAbilities"""
        logger.debug(f"[ChampionParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters the battlefield" not in lower or "exile" not in lower:
            return []
        
        m = CHAMPION_RE.search(reminder_text)
        if not m:
            return []
        
        champion_type = m.group(1).strip()
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="target", types=["permanent"]),
            from_zone="battlefield",
            to_zone="exile",
            owner="owner"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        conditional_effect = ConditionalEffect(
            condition="unless_you_exile",
            effects=[exile_effect]
        )
        
        etb_trigger = TriggeredAbility(
            condition_text=f"When this permanent enters the battlefield, sacrifice it unless you exile another {champion_type} you control.",
            effects=[conditional_effect, sacrifice_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="exiled_card"),
            from_zone="exile",
            to_zone="battlefield",
            owner="owner"
        )
        
        leaves_trigger = TriggeredAbility(
            condition_text="When this permanent leaves the battlefield, return the exiled card to the battlefield under its owner's control.",
            effects=[return_effect],
            event=LeavesBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ChampionParser] Created two TriggeredAbilities for Champion {champion_type}")
        
        return [etb_trigger, leaves_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Champion keyword without reminder text (e.g., 'Champion a creature')"""
        logger.debug(f"[ChampionParser] Parsing keyword only: {keyword_text}")
        
        m = CHAMPION_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ChampionParser] No champion type found in keyword text")
            return []
        
        champion_type = m.group(1).strip()
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="target", types=["permanent"]),
            from_zone="battlefield",
            to_zone="exile",
            owner="owner"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        conditional_effect = ConditionalEffect(
            condition="unless_you_exile",
            effects=[exile_effect]
        )
        
        etb_trigger = TriggeredAbility(
            condition_text=f"When this permanent enters the battlefield, sacrifice it unless you exile another {champion_type} you control.",
            effects=[conditional_effect, sacrifice_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="exiled_card"),
            from_zone="exile",
            to_zone="battlefield",
            owner="owner"
        )
        
        leaves_trigger = TriggeredAbility(
            condition_text="When this permanent leaves the battlefield, return the exiled card to the battlefield under its owner's control.",
            effects=[return_effect],
            event=LeavesBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ChampionParser] Created two TriggeredAbilities for Champion {champion_type}")
        
        return [etb_trigger, leaves_trigger]

