# axis2/parsing/keyword_abilities/transfigure.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, SearchEffect, Subject, ParseContext, Effect, SacrificeCost
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

TRANSFIGURE_RE = re.compile(
    r"transfigure\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class TransfigureParser:
    """Parses Transfigure keyword ability (activated ability)"""
    
    keyword_name = "transfigure"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Transfigure pattern"""
        lower = reminder_text.lower()
        return "sacrifice" in lower and "search your library" in lower and "same.*mana value" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Transfigure reminder text into ActivatedAbility"""
        logger.debug(f"[TransfigureParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "sacrifice" not in lower or "search your library" not in lower:
            return []
        
        m = TRANSFIGURE_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(SacrificeCost(subject=Subject(scope="self")))
        
        search_effect = SearchEffect(
            zones=["library"],
            card_names=None,
            optional=False,
            put_onto_battlefield=True,
            shuffle_if_library_searched=True,
            card_filter={"types": ["creature"], "mana_value": "same_as_this_permanent"},
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
        
        logger.debug(f"[TransfigureParser] Created ActivatedAbility for Transfigure")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Transfigure keyword without reminder text (e.g., 'Transfigure {1}{B}{B}')"""
        logger.debug(f"[TransfigureParser] Parsing keyword only: {keyword_text}")
        
        m = TRANSFIGURE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[TransfigureParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(SacrificeCost(subject=Subject(scope="self")))
        
        search_effect = SearchEffect(
            zones=["library"],
            card_names=None,
            optional=False,
            put_onto_battlefield=True,
            shuffle_if_library_searched=True,
            card_filter={"types": ["creature"], "mana_value": "same_as_this_permanent"},
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
        
        logger.debug(f"[TransfigureParser] Created ActivatedAbility for Transfigure {cost_text}")
        
        return [activated_ability]

