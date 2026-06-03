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
        logger.debug("[REPLACEMENT_DISPATCHER] Empty text, returning empty list")
        return effects

    logger.debug(f"[REPLACEMENT_DISPATCHER] Parsing replacement effects from: {text[:100]}")
    registry = get_registry()
    result = registry.parse(text)
    
    logger.debug(f"[REPLACEMENT_DISPATCHER] Parse result: matched={result.matched}, is_success={result.is_success}, errors={result.errors}")
    
    if result.is_success:
        effects.extend(result.all_effects)
        logger.debug(f"[REPLACEMENT_DISPATCHER] Successfully parsed {len(effects)} effects")
    else:
        logger.warning(f"[REPLACEMENT_DISPATCHER] Failed to parse replacement effect: {text[:50]}...")
        if result.errors:
            logger.debug(f"[REPLACEMENT_DISPATCHER] Errors: {result.errors}")

    return effects

