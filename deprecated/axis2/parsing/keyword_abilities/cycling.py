# axis2/parsing/keyword_abilities/cycling.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, DrawCardsEffect, DiscardCost, ParseContext, Effect, SearchEffect
from axis2.parsing.costs import parse_cost_string
from axis2.parsing.effects.dispatcher import parse_effect_text

logger = logging.getLogger(__name__)

CYCLING_RE = re.compile(
    r"(\w+)?cycling\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)

TYpecycling_KEYWORDS = [
    "islandcycling", "swampcycling", "mountaincycling", "forestcycling", "plaincycling",
    "basic landcycling", "wizardcycling", "slivercycling"
]


class CyclingParser:
    """Parses Cycling keyword ability (activated ability with cost)"""
    
    keyword_name = "cycling"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Cycling pattern"""
        lower = reminder_text.lower()
        return ("discard this card" in lower and "draw a card" in lower) or \
               ("discard this card" in lower and "search your library" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cycling reminder text into ActivatedAbility"""
        logger.debug(f"[CyclingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        
        m = CYCLING_RE.search(reminder_text)
        if not m:
            return []
        
        type_prefix = (m.group(1) or "").strip()
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(DiscardCost(amount=1))
        
        if "search your library" in lower or type_prefix:
            card_filter = {}
            if type_prefix:
                type_lower = type_prefix.lower()
                if "basic" in type_lower and "land" in type_lower:
                    card_filter = {"types": ["land"], "subtypes": ["basic"]}
                elif type_lower in ["island", "swamp", "mountain", "forest", "plains"]:
                    card_filter = {"subtypes": [type_lower]}
                else:
                    card_filter = {"subtypes": [type_lower]}
            
            effects = [
                SearchEffect(
                    zones=["library"],
                    card_names=None,
                    optional=False,
                    put_onto_battlefield=False,
                    shuffle_if_library_searched=True,
                    card_filter=card_filter if card_filter else None,
                    max_results=1
                )
            ]
        else:
            effects = [DrawCardsEffect(amount=1)]
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=None,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[CyclingParser] Created ActivatedAbility for {type_prefix or ''}cycling")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cycling keyword without reminder text (e.g., 'Cycling {2}')"""
        logger.debug(f"[CyclingParser] Parsing keyword only: {keyword_text}")
        
        m = CYCLING_RE.search(keyword_text)
        if not m:
            logger.debug(f"[CyclingParser] No cost found in keyword text")
            return []
        
        type_prefix = (m.group(1) or "").strip()
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(DiscardCost(amount=1))
        
        if type_prefix:
            type_lower = type_prefix.lower()
            card_filter = {}
            if "basic" in type_lower and "land" in type_lower:
                card_filter = {"types": ["land"], "subtypes": ["basic"]}
            elif type_lower in ["island", "swamp", "mountain", "forest", "plains"]:
                card_filter = {"subtypes": [type_lower]}
            else:
                card_filter = {"subtypes": [type_lower]}
            
            effects = [
                SearchEffect(
                    zones=["library"],
                    card_names=None,
                    optional=False,
                    put_onto_battlefield=False,
                    shuffle_if_library_searched=True,
                    card_filter=card_filter,
                    max_results=1
                )
            ]
        else:
            effects = [DrawCardsEffect(amount=1)]
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=None,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[CyclingParser] Created ActivatedAbility for {type_prefix or ''}cycling {cost_text}")
        
        return [activated_ability]

