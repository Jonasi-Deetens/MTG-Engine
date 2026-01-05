# axis2/parsing/ability_boundaries.py

"""
Ability boundary detection using syntactic markers.

This module identifies complete abilities in oracle text by detecting
syntactic markers (NOT punctuation). Magic's punctuation is not semantic.

Fundamental Rule: Abilities are the primary unit. Sentences are secondary.
"""

import re
from dataclasses import dataclass
from typing import List, Optional
from axis2.schema import ParseContext


@dataclass
class AbilityChunk:
    """Represents a complete ability chunk with its boundaries."""
    text: str  # Complete ability text (may be multi-sentence)
    type: str  # "triggered", "activated", "static", "replacement", "continuous", "spell", "unknown"
    start_marker: str  # The syntactic marker that started this ability
    line_indices: List[int]  # Original line numbers for debugging
    start_pos: int  # Character position in original text
    end_pos: int  # Character position in original text


# Triggered ability starters
TRIGGER_STARTERS = [
    r"^when\s+",
    r"^whenever\s+",
    r"^at\s+the\s+beginning",
    r"^at\s+the\s+end",
]

# Activated ability patterns - cost followed by colon
ACTIVATED_COST_PATTERNS = [
    r"^\{[^}]+\}",  # Mana symbols like {T}, {1}, {W}
    r"^tap\s+",  # "Tap"
    r"^untap\s+",  # "Untap"
    r"^pay\s+",  # "Pay"
    r"^sacrifice\s+",  # "Sacrifice"
    r"^discard\s+",  # "Discard"
    r"^exile\s+",  # "Exile"
    r"^return\s+",  # "Return"
    r"^reveal\s+",  # "Reveal"
    r"^mill\s+",  # "Mill"
    r"^remove\s+",  # "Remove"
]

# Static ability patterns - comprehensive list
STATIC_SUBJECT_PATTERNS = [
    r"^enchanted\s+creature",
    r"^equipped\s+creature",
    r"^creatures\s+you\s+control",
    r"^other\s+creatures\s+you\s+control",
    r"^creatures\s+your\s+opponents?\s+control",
    r"^this\s+creature",
    r"^this\s+permanent",
    r"^this\s+spell",
]

# Note: "Enchant creature" is NOT a static ability - it's a targeting restriction
# It should be handled separately by parse_enchant_restriction
# We do NOT include it in static ability patterns

STATIC_CONDITIONAL_PATTERNS = [
    r"^as\s+long\s+as",
    r"^if\s+",  # Conditional static ability (not triggered)
]

STATIC_RULE_PATTERNS = [
    r"^players\s+can't",
    r"^your\s+opponents?\s+can't",
    r"^you\s+may\s+look\s+at",
    r"^each\s+opponent",
    r"^you\s+may\s+play",
]

STATIC_COST_PATTERNS = [
    r"^this\s+spell\s+costs",
    r"^spells\s+you\s+cast\s+cost",
    r"^spells\s+your\s+opponents?\s+cast\s+cost",
]

STATIC_TYPE_PATTERNS = [
    r"\bare\s+",  # Type or color changes
    r"\bis\s+",  # Type or color changes
]

# Replacement effect patterns
REPLACEMENT_PATTERNS = [
    r"^if\s+.*\s+would\s+.*\s+instead",
    r"^prevent\s+",
    r"^enters\s+.*\s+with\s+",
]

# Mode separators
MODE_SEPARATORS = [
    r"^choose\s+one\s*[—\-]",
    r"^•\s*",
    r"^-\s*",
]

# Spell ability indicators
SPELL_ABILITY_PATTERNS = [
    r"^as\s+an\s+additional\s+cost\s+to\s+cast",
    r"^you\s+may\s+cast\s+this\s+spell\s+for",
]


def _is_trigger_start(line: str) -> bool:
    """Check if line starts a triggered ability (When, Whenever, At)."""
    line_lower = line.strip().lower()
    for pattern in TRIGGER_STARTERS:
        if re.match(pattern, line_lower):
            return True
    return False


def _is_activated_start(line: str) -> bool:
    """Check if line starts an activated ability (cost followed by colon)."""
    # Check for colon in the line
    if ":" not in line:
        return False
    
    # Split on colon to get cost part
    parts = line.split(":", 1)
    if len(parts) < 2:
        return False
    
    cost_part = parts[0].strip()
    if not cost_part:
        return False
    
    cost_lower = cost_part.lower()
    
    # Check for mana symbols
    if re.match(r"^\{[^}]+\}", cost_part):
        return True
    
    # Check for word-based costs
    for pattern in ACTIVATED_COST_PATTERNS:
        if re.match(pattern, cost_lower):
            return True
    
    # Check for generic cost pattern (word followed by colon)
    # This catches cases like "Equip {2}:" or "Activate only as a sorcery:"
    if re.match(r"^[a-z][a-z\s,]+:", cost_lower):
        return True
    
    return False


def _is_static_start(line: str, ctx: ParseContext) -> bool:
    """Check if line starts a static ability (patterns like 'Enchanted creature', 'As long as', etc.)."""
    line_lower = line.strip().lower()
    
    # NOTE: "Enchant creature" is NOT a static ability - it's a targeting restriction
    # We explicitly exclude it here (it should be handled separately by parse_enchant_restriction)
    if re.match(r"^enchant\s+(creature|artifact|land|planeswalker|enchantment|permanent|player|battle)(?:\s+with\s+.*)?\.?$", line_lower):
        return False
    
    # Subject-based patterns
    for pattern in STATIC_SUBJECT_PATTERNS:
        if re.match(pattern, line_lower):
            return True
    
    # Conditional patterns
    for pattern in STATIC_CONDITIONAL_PATTERNS:
        if re.match(pattern, line_lower):
            return True
    
    # Rule-changing patterns
    for pattern in STATIC_RULE_PATTERNS:
        if re.match(pattern, line_lower):
            return True
    
    # Cost modification patterns
    for pattern in STATIC_COST_PATTERNS:
        if re.match(pattern, line_lower):
            return True
    
    # Card name references
    card_name_lower = ctx.card_name.lower()
    if line_lower.startswith(card_name_lower + " is ") or \
       line_lower.startswith(card_name_lower + " has "):
        return True
    
    # Type/color changes (check if line contains these patterns)
    for pattern in STATIC_TYPE_PATTERNS:
        if re.search(pattern, line_lower):
            # Make sure it's not a triggered ability or activated ability
            if not _is_trigger_start(line) and not _is_activated_start(line):
                return True
    
    return False


def _is_replacement_start(line: str) -> bool:
    """Check if line starts a replacement effect."""
    line_lower = line.strip().lower()
    for pattern in REPLACEMENT_PATTERNS:
        if re.match(pattern, line_lower):
            return True
    return False


def _is_mode_separator(line: str) -> bool:
    """Check if line is a mode separator ('Choose one —', '•')."""
    line_lower = line.strip().lower()
    for pattern in MODE_SEPARATORS:
        if re.match(pattern, line_lower):
            return True
    return False


def _is_spell_ability_start(line: str) -> bool:
    """Check if line starts a spell ability (for instants/sorceries)."""
    line_lower = line.strip().lower()
    for pattern in SPELL_ABILITY_PATTERNS:
        if re.match(pattern, line_lower):
            return True
    return False


def _classify_ability_type(line: str, ctx: ParseContext) -> str:
    """Classify the type of ability based on the starting line."""
    if _is_trigger_start(line):
        return "triggered"
    elif _is_activated_start(line):
        return "activated"
    elif _is_replacement_start(line):
        return "replacement"
    elif _is_static_start(line, ctx):
        return "static"
    elif _is_spell_ability_start(line):
        return "spell"
    else:
        return "unknown"


def _find_next_ability_marker(lines: List[str], start_idx: int, ctx: ParseContext) -> int:
    """
    Find the index of the next ability marker after start_idx.
    Returns len(lines) if no marker found.
    """
    for i in range(start_idx + 1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        
        # Check for any ability marker
        if (_is_trigger_start(line) or
            _is_activated_start(line) or
            _is_replacement_start(line) or
            _is_static_start(line, ctx) or
            _is_mode_separator(line) or
            _is_spell_ability_start(line)):
            return i
    
    return len(lines)


def detect_ability_boundaries(text: str, ctx: ParseContext) -> List[AbilityChunk]:
    """
    Split oracle text into ability chunks using syntactic markers.
    
    Each chunk represents a complete ability (triggered, activated, static, etc.)
    Keywords are handled separately by keyword registry and should be removed
    from text before calling this function.
    
    Args:
        text: Oracle text (keywords should already be removed)
        ctx: ParseContext for card-specific information
        
    Returns:
        List of AbilityChunk objects representing complete abilities
    """
    if not text or not text.strip():
        return []
    
    chunks: List[AbilityChunk] = []
    lines = text.split("\n")
    
    i = 0
    char_pos = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            char_pos += len(lines[i-1]) + 1  # +1 for newline
            continue
        
        # Check if this line starts a new ability
        ability_type = _classify_ability_type(line, ctx)
        
        if ability_type == "unknown":
            # If we don't recognize this as an ability starter, it might be:
            # 1. A continuation of the previous ability
            # 2. Part of a multi-line ability
            # 3. A mode separator (which we handle separately)
            
            if _is_mode_separator(line):
                # Mode separator - treat as separate chunk
                start_pos = char_pos
                end_pos = char_pos + len(line)
                chunks.append(AbilityChunk(
                    text=line,
                    type="mode",
                    start_marker=line,
                    line_indices=[i],
                    start_pos=start_pos,
                    end_pos=end_pos
                ))
                i += 1
                char_pos = end_pos + 1
                continue
            
            # If we have a previous chunk, this might be a continuation
            if chunks and chunks[-1].type != "unknown":
                # Check if this looks like a continuation
                # (e.g., starts with "If you do", "Then", "It", "That creature")
                continuation_indicators = [
                    r"^if\s+you\s+do",
                    r"^then\s+",
                    r"^it\s+",
                    r"^that\s+creature",
                    r"^those\s+creatures",
                    r"^as\s+long\s+as",
                ]
                
                is_continuation = False
                line_lower = line.lower()
                for pattern in continuation_indicators:
                    if re.match(pattern, line_lower):
                        is_continuation = True
                        break
                
                # NOTE: "Enchant creature" is no longer detected as static,
                # so we don't need special handling for it here
                
                if is_continuation:
                    # Append to previous chunk
                    prev_chunk = chunks[-1]
                    prev_chunk.text += "\n" + line
                    prev_chunk.line_indices.append(i)
                    prev_chunk.end_pos = char_pos + len(line)
                    i += 1
                    char_pos += len(line) + 1
                    continue
            
            # Unknown line - create unknown chunk
            start_pos = char_pos
            end_pos = char_pos + len(line)
            chunks.append(AbilityChunk(
                text=line,
                type="unknown",
                start_marker="",
                line_indices=[i],
                start_pos=start_pos,
                end_pos=end_pos
            ))
            i += 1
            char_pos = end_pos + 1
            continue
        
        # This line starts a new ability
        # Find where this ability ends (next ability marker)
        start_pos = char_pos
        start_line_idx = i
        start_marker = line
        
        # Collect all lines until next ability marker
        ability_lines = [line]
        i += 1
        char_pos += len(line) + 1
        
        next_marker_idx = _find_next_ability_marker(lines, start_line_idx, ctx)
        
        # Collect all lines up to (but not including) the next marker
        # Special handling: for static abilities starting with "Enchant",
        # include lines starting with "Enchanted" even if they're also static
        while i < next_marker_idx:
            line = lines[i].strip()
            if line:  # Only add non-empty lines
                ability_lines.append(line)
            i += 1
            if i < len(lines):
                char_pos += len(lines[i-1]) + 1
        
        # NOTE: We don't need special handling for "Enchant" + "Enchanted" anymore
        # because "Enchant creature" is now excluded from static detection
        
        # Join lines into ability text
        ability_text = "\n".join(ability_lines)
        end_pos = char_pos - 1
        
        # Create chunk
        chunk = AbilityChunk(
            text=ability_text,
            type=ability_type,
            start_marker=start_marker,
            line_indices=list(range(start_line_idx, start_line_idx + len(ability_lines))),
            start_pos=start_pos,
            end_pos=end_pos
        )
        chunks.append(chunk)
    
    return chunks

