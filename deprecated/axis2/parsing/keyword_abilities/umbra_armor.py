# axis2/parsing/keyword_abilities/umbra_armor.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect
from axis2.parsing.replacement_effects.destruction import (
    parse_destruction_subject,
    parse_destruction_instead_actions
)
from axis2.parsing.replacement_effects.patterns import RE_WOULD_BE_DESTROYED

logger = logging.getLogger(__name__)


class UmbraArmorParser:
    """Parses Umbra armor keyword ability (replacement effect)"""
    
    keyword_name = "umbra armor"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains destruction replacement pattern"""
        lower = reminder_text.lower()
        return "would be destroyed" in lower and "instead" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Umbra armor reminder text into ReplacementEffect"""
        logger.debug(f"[UmbraArmorParser] Parsing reminder text: {reminder_text}")
        
        m = RE_WOULD_BE_DESTROYED.search(reminder_text)
        if not m:
            logger.warning(f"[UmbraArmorParser] Regex did not match reminder text: '{reminder_text}'")
            logger.warning(f"[UmbraArmorParser] Pattern: {RE_WOULD_BE_DESTROYED.pattern}")
            return []
        
        try:
            subject_raw = m.group(1).strip()
            action_raw = m.group(2).strip()
            
            subject = parse_destruction_subject(subject_raw)
            actions = parse_destruction_instead_actions(action_raw)
            
            logger.debug(f"[UmbraArmorParser] Parsed subject: {subject.scope}, actions: {actions}")
            
            effect = ReplacementEffect(
                kind="prevent_destruction",
                event="would_be_destroyed",
                subject=subject,
                value={"instead": actions},
                zones=["battlefield"],
                text=reminder_text
            )
            
            logger.debug(f"[UmbraArmorParser] Created ReplacementEffect: {effect.kind}")
            
            return [effect]
        except (ValueError, AttributeError) as e:
            logger.error(f"[UmbraArmorParser] Error parsing: {e}")
            return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Umbra armor always has reminder text, so this should not be called"""
        return []

