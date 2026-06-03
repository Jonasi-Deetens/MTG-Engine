# axis2/parsing/keyword_abilities/encore.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, CreateTokenEffect, ChangeZoneEffect, Subject, TriggeredAbility, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

ENCORE_RE = re.compile(
    r"encore\s+(.+)",
    re.IGNORECASE
)


class EncoreParser:
    """Parses Encore keyword ability (activated ability)"""
    
    keyword_name = "encore"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Encore pattern"""
        lower = reminder_text.lower()
        return "exile this card" in lower and "graveyard" in lower and "create a token copy" in lower and "opponent" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Encore reminder text into ActivatedAbility"""
        logger.debug(f"[EncoreParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile this card" not in lower or "create a token copy" not in lower:
            return []
        
        m = ENCORE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[EncoreParser] No encore cost found in reminder text")
            return []
        
        cost_text = m.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        create_token_effect = CreateTokenEffect(
            amount="number_of_opponents",
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "attacking": True,
                "abilities": ["haste"]
            },
            controller="you"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="created_tokens"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, sacrifice the tokens created by encore.",
            effects=[sacrifice_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[exile_effect, create_token_effect],
            conditions=[{"kind": "exile_self_from_graveyard_as_cost"}, {"kind": "activate_only_as_sorcery"}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[EncoreParser] Created ActivatedAbility and TriggeredAbility for Encore")
        
        return [activated_ability, end_step_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Encore keyword without reminder text (e.g., 'Encore {3}{B}')"""
        logger.debug(f"[EncoreParser] Parsing keyword only: {keyword_text}")
        
        m = ENCORE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[EncoreParser] No encore cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        create_token_effect = CreateTokenEffect(
            amount="number_of_opponents",
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "attacking": True,
                "abilities": ["haste"]
            },
            controller="you"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="created_tokens"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        end_step_trigger = TriggeredAbility(
            condition_text="At the beginning of the next end step, sacrifice the tokens created by encore.",
            effects=[sacrifice_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[exile_effect, create_token_effect],
            conditions=[{"kind": "exile_self_from_graveyard_as_cost"}, {"kind": "activate_only_as_sorcery"}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[EncoreParser] Created ActivatedAbility and TriggeredAbility for Encore")
        
        return [activated_ability, end_step_trigger]

