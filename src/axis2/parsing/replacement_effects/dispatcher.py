# axis2/parsing/replacement_effects/dispatcher.py

from typing import List
from .base import ParseResult
from .registry import get_registry
from axis2.schema import ReplacementEffect
import logging

logger = logging.getLogger(__name__)

def parse_replacement_effects(text: str) -> List[ReplacementEffect]:
    """
    Main entry point - replaces the old parse_replacement_effects.
    Now uses registry pattern instead of hardcoded chain.
    """
    effects = []
    if not text:
        return effects

    registry = get_registry()
    result = registry.parse(text)
    
    if result.is_success:
        effects.extend(result.all_effects)
    else:
        logger.warning(f"Failed to parse replacement effect: {text[:50]}...")
        if result.errors:
            logger.debug(f"Errors: {result.errors}")

    return effects

