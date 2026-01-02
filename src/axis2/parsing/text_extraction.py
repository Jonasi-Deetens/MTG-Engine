"""
Smart text extraction that avoids duplication between Axis1 parsing and text parsing.

This module provides functions to extract remaining text for parsing after
structured abilities have been parsed from Axis1.
"""

import re
from typing import List
from axis1.schema import Axis1Face
from axis2.schema import ActivatedAbility, TriggeredAbility
from axis2.parsing.keywords import extract_keywords
from axis2.parsing.sentences import split_into_sentences


def get_remaining_text_for_parsing(
    face: Axis1Face,
    activated: List[ActivatedAbility],
    triggered: List[TriggeredAbility]
) -> str:
    """
    Get text that hasn't been parsed yet.
    
    Removes:
    - Activated abilities (from Axis1 or detected)
    - Triggered abilities (from Axis1 or detected)
    - Keywords (handled separately)
    
    Leaves:
    - Static abilities
    - Continuous effects
    - Replacement effects
    - Spell effects
    - Special actions (handled separately)
    
    Args:
        face: The Axis1Face to extract text from
        activated: Already parsed activated abilities
        triggered: Already parsed triggered abilities
        
    Returns:
        Cleaned text ready for further parsing
    """
    text = (face.oracle_text or "").strip()
    if not text:
        return ""
    
    # Remove activated abilities from Axis1
    for a in getattr(face, "activated_abilities", []):
        cost = getattr(a, "cost", "") or getattr(a, "cost_text", "") or ""
        effect = getattr(a, "effect", "") or getattr(a, "effect_text", "") or ""
        text = _remove_ability_text(text, cost, effect)
    
    # Remove triggered abilities from Axis1
    for t in getattr(face, "triggered_abilities", []):
        cond = (t.condition or "").strip()
        eff = (t.effect or "").strip()
        text = _remove_ability_text(text, cond, eff)
    
    # Remove standalone keyword lines
    keywords = extract_keywords(text)
    lines = text.split("\n")
    cleaned_lines = [
        line for line in lines
        if line.strip().lower() not in [kw.lower() for kw in keywords]
    ]
    text = "\n".join(cleaned_lines)
    
    return text.strip()


def _remove_ability_text(text: str, part1: str, part2: str) -> str:
    """
    Remove an ability text pattern from the text.
    
    Args:
        text: The text to clean
        part1: First part (cost or condition)
        part2: Second part (effect)
        
    Returns:
        Text with the ability removed
    """
    if not part1 and not part2:
        return text
    
    # Try different patterns
    patterns = []
    
    # Pattern 1: "PART1, PART2"
    if part1 and part2:
        combined = f"{part1}, {part2}".strip()
        if combined:
            escaped = re.escape(combined.rstrip("."))
            patterns.append(escaped + r"\.?\s*")
    
    # Pattern 2: "PART1: PART2" (for activated)
    if part1 and part2 and ":" in part1:
        combined = f"{part1} {part2}".strip()
        if combined:
            escaped = re.escape(combined.rstrip("."))
            patterns.append(escaped + r"\.?\s*")
    
    # Pattern 3: Just part1 (if it's a complete sentence)
    if part1 and not part2:
        escaped = re.escape(part1.rstrip("."))
        patterns.append(escaped + r"\.?\s*")
    
    # Apply all patterns
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    return text.strip()

