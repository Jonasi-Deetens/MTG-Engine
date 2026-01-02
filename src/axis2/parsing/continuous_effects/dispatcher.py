# axis2/parsing/continuous_effects/dispatcher.py

from typing import List, Optional
from .base import ParseResult
from .registry import get_registry
from .utils import split_continuous_clauses, guess_applies_to, detect_duration
from axis2.schema import ContinuousEffect, ParseContext
from axis2.parsing.conditions import parse_condition, extract_condition_text
import logging

logger = logging.getLogger(__name__)

def parse_continuous_effects(text: str, ctx: ParseContext) -> List[ContinuousEffect]:
    """
    Main entry point - replaces the old parse_continuous_effects.
    Now uses registry pattern instead of hardcoded chain.
    """
    effects = []
    if not text:
        return effects

    # Split into semantic clauses
    clauses = split_continuous_clauses(text)
    current_subject = None

    registry = get_registry()

    for clause in clauses:
        # 1. Conditional wrapper
        condition = None
        condition, clause = extract_condition_text(clause)
        # Try to parse structured card-type-count conditions (Delirium-like)
        structured = parse_condition(condition) if condition else None
        if structured:
            condition = structured

        applies_to = guess_applies_to(clause)

        if applies_to is None:
            applies_to = current_subject
        else:
            current_subject = applies_to

        # Detect duration
        duration = detect_duration(clause)

        # Use registry to find matching parser
        result = registry.parse(clause, ctx, applies_to, condition, duration)
        if result.is_success:
            effects.extend(result.all_effects)
        else:
            logger.warning(f"Failed to parse continuous effect: {clause[:50]}...")
            if result.errors:
                logger.debug(f"Errors: {result.errors}")

    return effects

