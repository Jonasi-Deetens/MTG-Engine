"""
Smart text extraction that avoids duplication between Axis1 parsing and text parsing.

This module provides functions to extract remaining text for parsing after
structured abilities have been parsed from Axis1.
"""

import re
import logging
from typing import List, Tuple, Optional
from axis1.schema import Axis1Face
from axis2.schema import ActivatedAbility, TriggeredAbility, Effect, ParseContext
from axis2.parsing.keywords import extract_keywords
from axis2.parsing.sentences import split_into_sentences

logger = logging.getLogger(__name__)


def get_remaining_text_for_parsing(
    face: Axis1Face,
    activated: List[ActivatedAbility],
    triggered: List[TriggeredAbility],
    ctx: Optional[ParseContext] = None
) -> Tuple[str, List[str], List[Effect]]:
    """
    Get text that hasn't been parsed yet.
    
    Removes:
    - Activated abilities (from Axis1 or detected)
    - Triggered abilities (from Axis1 or detected)
    - Keyword abilities (parsed and removed)
    
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
        ctx: ParseContext for keyword parsing
        
    Returns:
        Tuple of (cleaned_text, keyword_names, keyword_effects):
        - cleaned_text: Text ready for further parsing
        - keyword_names: List of keyword names found
        - keyword_effects: List of Effect objects from keyword abilities
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
    
    # Parse keyword abilities FIRST and remove their lines from text
    keyword_names = []
    keyword_effects = []
    keyword_lines_to_remove = []
    
    if ctx is not None:
        from axis2.parsing.keyword_abilities import get_registry
        registry = get_registry()
        
        lines = text.split("\n")
        cleaned_lines = []
        
        logger.debug(f"[TEXT_EXTRACT] Original text: {text[:200]}")
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                cleaned_lines.append(line)
                continue
            
            # Check if this line is a keyword
            keyword_result = registry.detect_keyword(stripped)
            if keyword_result:
                keyword_name, reminder_text, cost_text = keyword_result
                print(f"[TEXT_EXTRACT PRINT] Line '{stripped}' detected as keyword: {keyword_name}")
                logger.debug(f"[TEXT_EXTRACT] Found keyword: {keyword_name}, reminder: {reminder_text[:50] if reminder_text else None}")
                
                # Parse the keyword ability
                parsed_effects = registry.parse_keyword(
                    keyword_name, reminder_text, cost_text, stripped, ctx
                )
                
                keyword_names.append(keyword_name)
                keyword_effects.extend(parsed_effects)
                keyword_lines_to_remove.append(stripped)
                
                # Don't add this line to cleaned_lines (it's been parsed)
                continue
            
            # Keep non-keyword lines
            cleaned_lines.append(stripped)
        
        text = "\n".join(cleaned_lines)
        print(f"[TEXT_EXTRACT PRINT] Removed {len(keyword_lines_to_remove)} keyword lines")
        print(f"[TEXT_EXTRACT PRINT] Parsed {len(keyword_effects)} keyword effects")
        print(f"[TEXT_EXTRACT PRINT] Remaining text after keyword removal: {text[:300]}")
        logger.debug(f"[TEXT_EXTRACT] Removed {len(keyword_lines_to_remove)} keyword lines")
        logger.debug(f"[TEXT_EXTRACT] Parsed {len(keyword_effects)} keyword effects")
        logger.debug(f"[TEXT_EXTRACT] Remaining text after keyword removal: {text[:300]}")
    
    # Extract parenthetical text (for non-keyword parentheticals)
    parenthetical_text = []
    lines = text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(line)
            continue
        
        # Extract parenthetical text (e.g., "(If X would be destroyed...)")
        # But skip if it's part of a keyword line (already handled above)
        paren_match = re.search(r"\(([^)]+)\)", stripped)
        if paren_match:
            extracted = paren_match.group(1)
            logger.debug(f"[TEXT_EXTRACT] Found parenthetical text: {extracted[:100]}")
            parenthetical_text.append(extracted)
            # Remove the parenthetical part from the line
            line_without_paren = re.sub(r"\([^)]+\)", "", stripped).strip()
            # If line still has content after removing parenthetical, keep it
            if line_without_paren:
                cleaned_lines.append(line_without_paren)
        else:
            cleaned_lines.append(stripped)
    
    # Remove standalone keyword lines (simple keywords without reminder text)
    keywords = extract_keywords("\n".join(cleaned_lines))
    logger.debug(f"[TEXT_EXTRACT] Extracted simple keywords: {keywords}")
    logger.debug(f"[TEXT_EXTRACT] Lines before keyword removal: {cleaned_lines}")
    cleaned_lines = [
        line for line in cleaned_lines
        if line.lower() not in [kw.lower() for kw in keywords]
    ]
    logger.debug(f"[TEXT_EXTRACT] Lines after keyword removal: {cleaned_lines}")
    
    # Add back parenthetical text as separate lines (for non-keyword parentheticals)
    if parenthetical_text:
        logger.debug(f"[TEXT_EXTRACT] Adding {len(parenthetical_text)} parenthetical text lines back")
        cleaned_lines.extend(parenthetical_text)
    
    text = "\n".join(cleaned_lines)
    logger.debug(f"[TEXT_EXTRACT] Final remaining text: {text[:200]}")
    
    return text.strip(), keyword_names, keyword_effects


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

