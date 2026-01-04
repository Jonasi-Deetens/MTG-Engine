# axis2/parsing/triggers/dispatcher.py

from typing import Optional, Union
from .base import ParseResult
from .registry import get_registry
from axis2.schema import (
    ZoneChangeEvent, DealsDamageEvent, EntersBattlefieldEvent,
    AttacksEvent, LeavesBattlefieldEvent, CastSpellEvent, DiesEvent
)
import logging

logger = logging.getLogger(__name__)

def parse_trigger_event(condition_text: str) -> Optional[Union[ZoneChangeEvent, DealsDamageEvent, 
                                                               EntersBattlefieldEvent, AttacksEvent,
                                                               LeavesBattlefieldEvent, CastSpellEvent, DiesEvent, str]]:
    """
    Main entry point - replaces the old parse_trigger_event.
    Now uses registry pattern instead of hardcoded chain.
    """
    if not condition_text:
        return None

    registry = get_registry()
    result = registry.parse(condition_text)
    
    if result.is_success:
        return result.event
    else:
        logger.warning(f"Failed to parse trigger event: {condition_text[:50]}...")
        if result.errors:
            logger.debug(f"Errors: {result.errors}")
        return None

