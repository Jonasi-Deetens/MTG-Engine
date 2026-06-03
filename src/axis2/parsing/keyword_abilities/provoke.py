# axis2/parsing/keyword_abilities/provoke.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ParseContext, Effect, TargetingRules, TargetingRestriction
from axis2.parsing.effects.dispatcher import parse_effect_text
from axis2.parsing.targeting import parse_targeting

logger = logging.getLogger(__name__)


class ProvokeParser:
    """Parses Provoke keyword ability (triggered ability)"""
    
    keyword_name = "provoke"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Provoke pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and ("block" in lower or "untap" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Provoke reminder text into TriggeredAbility"""
        logger.debug(f"[ProvokeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or ("block" not in lower and "untap" not in lower):
            return []
        
        condition_text = "Whenever this creature attacks, you may choose to have target creature defending player controls block this creature this combat if able. If you do, untap that creature."
        
        effect_text = "Target creature defending player controls untaps and must block this creature this combat if able."
        effects = parse_effect_text(effect_text, ctx)
        
        targeting = parse_targeting(effect_text)
        if not targeting:
            targeting = TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["creature"],
                restrictions=[TargetingRestriction(type="controller", conditions=[{"controller": "defending_player"}])]
            )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event="attacks",
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[ProvokeParser] Created TriggeredAbility for Provoke")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Provoke keyword without reminder text"""
        logger.debug(f"[ProvokeParser] Parsing keyword only: {keyword_text}")
        
        condition_text = "Whenever this creature attacks, you may choose to have target creature defending player controls block this creature this combat if able. If you do, untap that creature."
        
        effect_text = "Target creature defending player controls untaps and must block this creature this combat if able."
        effects = parse_effect_text(effect_text, ctx)
        
        targeting = parse_targeting(effect_text)
        if not targeting:
            targeting = TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["creature"],
                restrictions=[TargetingRestriction(type="controller", conditions=[{"controller": "defending_player"}])]
            )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event="attacks",
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[ProvokeParser] Created TriggeredAbility for Provoke")
        
        return [triggered_ability]

