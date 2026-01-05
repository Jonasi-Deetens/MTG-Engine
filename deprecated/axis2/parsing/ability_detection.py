"""
Ability type detection and classification.

This module provides functions to detect and classify different types of
MTG abilities from text.
"""

import re
from typing import Optional


# Patterns for detecting ability types
ACTIVATED_PATTERN = re.compile(r"^\{[^}]+\}.*:", re.IGNORECASE)  # "{COST}: EFFECT"
TRIGGERED_PATTERN = re.compile(r"^(when|whenever|at)\s+", re.IGNORECASE)  # "When/Whenever/At ..."
REPLACEMENT_PATTERN = re.compile(r"if\s+.*\s+would\s+.*\s+instead", re.IGNORECASE)  # "If X would happen, Y instead"
CONTINUOUS_PATTERN = re.compile(
    r"(gets?\s+[+\-]?\d+/[+\-]?\d+|has\s+\w+|gains?\s+\w+|is\s+\w+|can't\s+be\s+blocked)",
    re.IGNORECASE
)  # "gets +1/+1", "has flying", "gains haste", etc.
MANA_ABILITY_PATTERN = re.compile(
    r"(add|produces?)\s+.*\s+mana",
    re.IGNORECASE
)  # "add mana", "produces mana"


def detect_ability_type(text: str) -> str:
    """
    Detect the type of ability from text.
    
    Returns one of:
    - "activated": "{COST}: EFFECT"
    - "triggered": "When/Whenever/At ..."
    - "static": Everything else on permanents
    - "mana_ability": Activated that produces mana
    - "replacement": "If X would happen, Y instead"
    - "continuous": "gets +1/+1", "has flying", etc.
    - "unknown": Could not determine
    
    Args:
        text: The ability text to classify
        
    Returns:
        The detected ability type
    """
    text = text.strip()
    if not text:
        return "unknown"
    
    # Check for activated ability pattern
    if ACTIVATED_PATTERN.match(text):
        # Check if it's a mana ability
        if is_mana_ability(text):
            return "mana_ability"
        return "activated"
    
    # Check for triggered ability pattern
    if TRIGGERED_PATTERN.match(text):
        return "triggered"
    
    # Check for replacement effect pattern
    if REPLACEMENT_PATTERN.search(text):
        return "replacement"
    
    # Check for continuous effect pattern
    if CONTINUOUS_PATTERN.search(text):
        return "continuous"
    
    # Default to static for permanents (will be determined by context)
    return "static"


def is_mana_ability(text: str) -> bool:
    """
    Check if an activated ability is a mana ability.
    
    A mana ability is an activated ability that:
    - Produces mana
    - Has no targets
    - Has no non-mana effects
    
    Args:
        text: The ability text to check
        
    Returns:
        True if this appears to be a mana ability
    """
    text_lower = text.lower()
    
    # Must produce or add mana
    if not MANA_ABILITY_PATTERN.search(text_lower):
        return False
    
    # Must not have targets (mana abilities can't target)
    if "target" in text_lower:
        return False
    
    # Must not have other effects (just mana production)
    # Simple heuristic: if it's just "add mana" or similar, it's likely a mana ability
    # More complex abilities with multiple effects are not mana abilities
    if "and" in text_lower and "mana" not in text_lower.split("and")[1]:
        return False
    
    return True


def is_activated_ability(text: str) -> bool:
    """Check if text represents an activated ability."""
    return ACTIVATED_PATTERN.match(text) is not None


def is_triggered_ability(text: str) -> bool:
    """Check if text represents a triggered ability."""
    return TRIGGERED_PATTERN.match(text) is not None


def is_replacement_effect(text: str) -> bool:
    """Check if text represents a replacement effect."""
    return REPLACEMENT_PATTERN.search(text) is not None


def is_continuous_effect(text: str) -> bool:
    """Check if text represents a continuous effect."""
    return CONTINUOUS_PATTERN.search(text) is not None

