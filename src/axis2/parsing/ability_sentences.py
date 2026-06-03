# axis2/parsing/ability_sentences.py

"""
Sentence splitting within ability boundaries.

This module splits ability chunks into atomic effect clauses while
preserving semantic relationships between sentences.
"""

import re
from dataclasses import dataclass
from typing import List, Optional
from axis2.parsing.ability_boundaries import AbilityChunk


@dataclass
class Sentence:
    """Represents a single sentence/clause within an ability."""
    text: str  # Single sentence/clause
    index: int  # Position within ability
    is_continuation: bool  # True if this continues previous sentence
    continuation_type: Optional[str]  # "if_you_do", "then", "pronoun", "as_long_as", etc.


# Continuation clause patterns
CONTINUATION_PATTERNS = {
    "if_you_do": [
        r"^if\s+you\s+do",
        r"^if\s+you\s+don't",
    ],
    "then": [
        r"^then\s+",
    ],
    "pronoun": [
        r"^it\s+",
        r"^that\s+creature",
        r"^those\s+creatures",
        r"^they\s+",
        r"^them\s+",
    ],
    "as_long_as": [
        r"^as\s+long\s+as",
    ],
    "otherwise": [
        r"^otherwise\s+",
    ],
    "instead": [
        r"^instead\s+",
    ],
}


def _is_continuation_clause(sentence: str) -> tuple[bool, Optional[str]]:
    """
    Check if sentence continues previous (e.g., "Then", "It", "That creature").
    
    Returns:
        Tuple of (is_continuation, continuation_type)
    """
    sentence_lower = sentence.strip().lower()
    
    for continuation_type, patterns in CONTINUATION_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, sentence_lower):
                return True, continuation_type
    
    return False, None


def _should_keep_with_previous(sentence: str, previous: str) -> bool:
    """
    Check if sentence should be kept with previous (e.g., "If you do").
    
    This is used to determine if a sentence should be merged with the
    previous sentence rather than split.
    """
    is_cont, _ = _is_continuation_clause(sentence)
    return is_cont


def split_ability_into_sentences(chunk: AbilityChunk) -> List[Sentence]:
    """
    Split an ability chunk into atomic effect clauses.
    
    Uses semantic awareness to keep related sentences together.
    Handles special cases like "If you do", "Then", pronoun references, etc.
    
    Args:
        chunk: AbilityChunk to split
        
    Returns:
        List of Sentence objects
    """
    if not chunk.text:
        return []
    
    # For activated abilities, extract only the effect text (after the colon)
    # This prevents the cost from being included in effect parsing
    text = chunk.text
    if chunk.type == "activated" and ":" in text:
        # Split on colon to get effect part only
        parts = text.split(":", 1)
        if len(parts) == 2:
            text = parts[1].strip()  # Use only the effect text, not the cost
    
    # First, split on periods and newlines
    # But we need to be careful about abbreviations and decimal numbers
    
    # Replace em-dashes with periods (they often separate clauses)
    text = text.replace("—", ". ")
    
    # Split on periods or newlines, but preserve the periods in the split
    # We'll use a regex that matches periods followed by space or newline
    parts = re.split(r"\.\s+|\n+", text)
    
    # Clean up and filter empty parts
    raw_sentences = [p.strip() for p in parts if p.strip()]
    
    if not raw_sentences:
        return []
    
    sentences: List[Sentence] = []
    
    for i, raw_sentence in enumerate(raw_sentences):
        # Check if this is a continuation of the previous sentence
        is_cont, cont_type = _is_continuation_clause(raw_sentence)
        
        # If it's a continuation and we have a previous sentence,
        # we might want to merge them, but for now we'll keep them separate
        # and mark the continuation relationship
        sentence = Sentence(
            text=raw_sentence,
            index=i,
            is_continuation=is_cont,
            continuation_type=cont_type
        )
        sentences.append(sentence)
    
    # Post-process: merge sentences that should be kept together
    # For example, "If you do" clauses should be merged with previous
    merged_sentences: List[Sentence] = []
    
    i = 0
    while i < len(sentences):
        current = sentences[i]
        
        # Check if next sentence is a continuation that should be merged
        if (i + 1 < len(sentences) and
            sentences[i + 1].is_continuation and
            sentences[i + 1].continuation_type in ["if_you_do", "then", "as_long_as"]):
            
            # Merge with next sentence
            merged_text = current.text + ". " + sentences[i + 1].text
            merged = Sentence(
                text=merged_text,
                index=current.index,
                is_continuation=current.is_continuation,
                continuation_type=current.continuation_type
            )
            merged_sentences.append(merged)
            i += 2  # Skip the merged sentence
        else:
            merged_sentences.append(current)
            i += 1
    
    return merged_sentences

