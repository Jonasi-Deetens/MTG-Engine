# axis2/parsing/keyword_abilities/transmute.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, SearchEffect, Subject, ParseContext, Effect, TargetingRules, DiscardCost
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

TRANSMUTE_RE = re.compile(
    r"transmute\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class TransmuteParser:
    """Parses Transmute keyword ability (activated ability)"""
    
    keyword_name = "transmute"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Transmute pattern"""
        lower = reminder_text.lower()
        return "discard this card" in lower and "search your library" in lower and "same.*mana value" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Transmute reminder text into ActivatedAbility"""
        logger.debug(f"[TransmuteParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "discard this card" not in lower or "search your library" not in lower:
            return []
        
        m = TRANSMUTE_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(DiscardCost(amount=1))
        
        search_effect = SearchEffect(
            zones=["library"],
            card_names=None,
            optional=False,
            put_onto_battlefield=False,
            shuffle_if_library_searched=True,
            card_filter={"mana_value": "same_as_this_card"},
            max_results=1
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[search_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[TransmuteParser] Created ActivatedAbility for Transmute")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Transmute keyword without reminder text (e.g., 'Transmute {1}{U}{U}')"""
        logger.debug(f"[TransmuteParser] Parsing keyword only: {keyword_text}")
        
        m = TRANSMUTE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[TransmuteParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(DiscardCost(amount=1))
        
        search_effect = SearchEffect(
            zones=["library"],
            card_names=None,
            optional=False,
            put_onto_battlefield=False,
            shuffle_if_library_searched=True,
            card_filter={"mana_value": "same_as_this_card"},
            max_results=1
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[search_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[TransmuteParser] Created ActivatedAbility for Transmute {cost_text}")
        
        return [activated_ability]

