# axis2/parsing/keyword_abilities/forecast.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string
from axis2.parsing.effects.dispatcher import parse_effect_text

logger = logging.getLogger(__name__)

FORECAST_RE = re.compile(
    r"forecast\s*—\s*(.+)",
    re.IGNORECASE
)


class ForecastParser:
    """Parses Forecast keyword ability (activated ability from hand)"""
    
    keyword_name = "forecast"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Forecast pattern"""
        lower = reminder_text.lower()
        return "reveal" in lower and "hand" in lower and ("upkeep" in lower or "once each turn" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Forecast reminder text into ActivatedAbility"""
        logger.debug(f"[ForecastParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "reveal" not in lower or "hand" not in lower:
            return []
        
        m = FORECAST_RE.search(reminder_text)
        if not m:
            return []
        
        ability_text = m.group(1).strip()
        
        colon_idx = ability_text.find(":")
        if colon_idx == -1:
            logger.debug(f"[ForecastParser] No colon found in forecast ability text")
            return []
        
        cost_text = ability_text[:colon_idx].strip()
        effect_text = ability_text[colon_idx + 1:].strip()
        
        costs = parse_cost_string(cost_text)
        
        effects = parse_effect_text(effect_text, ctx)
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=["during_upkeep", "once_per_turn"],
            targeting=None,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[ForecastParser] Created ActivatedAbility for Forecast")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Forecast keyword without reminder text (e.g., 'Forecast — {2}{W}{U}, Reveal...')"""
        logger.debug(f"[ForecastParser] Parsing keyword only: {keyword_text}")
        
        m = FORECAST_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ForecastParser] No forecast ability found in keyword text")
            return []
        
        ability_text = m.group(1).strip()
        
        colon_idx = ability_text.find(":")
        if colon_idx == -1:
            logger.debug(f"[ForecastParser] No colon found in forecast ability text")
            return []
        
        cost_text = ability_text[:colon_idx].strip()
        effect_text = ability_text[colon_idx + 1:].strip()
        
        costs = parse_cost_string(cost_text)
        
        effects = parse_effect_text(effect_text, ctx)
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=["during_upkeep", "once_per_turn"],
            targeting=None,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[ForecastParser] Created ActivatedAbility for Forecast")
        
        return [activated_ability]

