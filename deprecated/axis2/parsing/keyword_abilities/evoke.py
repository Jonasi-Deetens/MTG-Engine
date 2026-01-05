# axis2/parsing/keyword_abilities/evoke.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, EntersBattlefieldEvent, ChangeZoneEffect, Subject, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

EVOKE_RE = re.compile(
    r"evoke\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class EvokeParser:
    """Parses Evoke keyword ability (static ability + triggered ability)"""
    
    keyword_name = "evoke"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Evoke pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "evoke cost" in lower and "sacrificed" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Evoke reminder text into ReplacementEffect and TriggeredAbility"""
        logger.debug(f"[EvokeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "evoke cost" not in lower:
            return []
        
        m = EVOKE_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        replacement_effect = ReplacementEffect(
            kind="alternative_cost",
            event="would_cast",
            subject=Subject(scope="self"),
            value={"cost": costs},
            zones=["hand", "graveyard", "exile"]
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent enters the battlefield, if its evoke cost was paid, its controller sacrifices it.",
            effects=[sacrifice_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
        )
        
        logger.debug(f"[EvokeParser] Created ReplacementEffect and TriggeredAbility for Evoke")
        
        return [replacement_effect, triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Evoke keyword without reminder text (e.g., 'Evoke {W}')"""
        logger.debug(f"[EvokeParser] Parsing keyword only: {keyword_text}")
        
        m = EVOKE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[EvokeParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        replacement_effect = ReplacementEffect(
            kind="alternative_cost",
            event="would_cast",
            subject=Subject(scope="self"),
            value={"cost": costs},
            zones=["hand", "graveyard", "exile"]
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent enters the battlefield, if its evoke cost was paid, its controller sacrifices it.",
            effects=[sacrifice_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
        )
        
        logger.debug(f"[EvokeParser] Created ReplacementEffect and TriggeredAbility for Evoke {cost_text}")
        
        return [replacement_effect, triggered_ability]

