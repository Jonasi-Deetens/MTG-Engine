# axis2/parsing/effect_chains.py

"""
Effect chain reconstruction using semantic heuristics.

This module reconstructs effect chains from sentences, handling:
- Conditional effects ("If you do")
- Sequencing ("Then")
- Pronoun references ("It", "That creature", "Those creatures")
- "As long as" conditionals
"""

import re
from typing import List, Optional
from axis2.schema import Effect, ConditionalEffect, ParseContext
from axis2.parsing.ability_sentences import Sentence
from axis2.parsing.conditional_effects import parse_conditional
from axis2.parsing.effects import parse_effect_text


def _resolve_pronoun_reference(
    sentence: str,
    previous_sentences: List[Sentence],
    ctx: ParseContext
) -> str:
    """
    Resolve "It", "That creature", "Those creatures" to actual subjects.
    
    This is a heuristic-based resolution that looks at previous sentences
    to determine what the pronoun refers to.
    
    Args:
        sentence: Sentence containing pronoun reference
        previous_sentences: Previous sentences in the ability
        ctx: ParseContext for card information
        
    Returns:
        Resolved sentence with pronoun replaced (if possible)
    """
    sentence_lower = sentence.lower()
    
    # Common pronoun patterns
    pronoun_patterns = [
        (r"\bit\s+", "it"),
        (r"\bthat\s+creature\s+", "that creature"),
        (r"\bthose\s+creatures\s+", "those creatures"),
        (r"\bthey\s+", "they"),
        (r"\bthem\s+", "them"),
    ]
    
    # Look for subject in previous sentences
    # Common patterns: "target creature", "enchanted creature", "creatures you control"
    resolved = sentence
    
    for pattern, pronoun in pronoun_patterns:
        if re.search(pattern, sentence_lower):
            # Try to find subject in previous sentences
            for prev_sentence in reversed(previous_sentences):
                prev_lower = prev_sentence.text.lower()
                
                # Check for common subject patterns
                subject_patterns = [
                    r"target\s+creature",
                    r"enchanted\s+creature",
                    r"equipped\s+creature",
                    r"creatures\s+you\s+control",
                    r"that\s+creature",
                    r"this\s+creature",
                    r"this\s+permanent",
                ]
                
                for subj_pattern in subject_patterns:
                    match = re.search(subj_pattern, prev_lower)
                    if match:
                        # Replace pronoun with found subject
                        resolved = re.sub(
                            pattern,
                            match.group(0) + " ",
                            resolved,
                            flags=re.IGNORECASE
                        )
                        break
                
                if resolved != sentence:
                    break
            
            # If no subject found, try card name
            if resolved == sentence and pronoun == "it":
                # "It" might refer to the card itself
                if "aura" in ctx.primary_type.lower():
                    resolved = re.sub(pattern, "this Aura ", resolved, flags=re.IGNORECASE)
                elif "equipment" in ctx.primary_type.lower():
                    resolved = re.sub(pattern, "this Equipment ", resolved, flags=re.IGNORECASE)
                elif "creature" in ctx.primary_type.lower():
                    resolved = re.sub(pattern, "this creature ", resolved, flags=re.IGNORECASE)
                else:
                    resolved = re.sub(pattern, ctx.card_name + " ", resolved, flags=re.IGNORECASE)
    
    return resolved


def _link_conditional_effect(
    sentences: List[Sentence],
    index: int,
    ctx: ParseContext
) -> Optional[ConditionalEffect]:
    """
    Link "If you do" clause to previous effect.
    
    Args:
        sentences: List of all sentences
        index: Index of the "If you do" sentence
        ctx: ParseContext
        
    Returns:
        ConditionalEffect if successfully linked, None otherwise
    """
    if index == 0:
        return None  # No previous sentence
    
    current = sentences[index]
    previous = sentences[index - 1]
    
    # Check if current sentence is "If you do"
    if current.continuation_type != "if_you_do":
        return None
    
    # Parse the conditional effect from the current sentence
    conditional = parse_conditional(current.text, ctx)
    
    if conditional:
        # Try to parse the previous sentence as effects
        prev_effects = parse_effect_text(previous.text, ctx)
        
        if prev_effects:
            # The conditional effect should reference the previous effects
            # For now, we'll return the conditional as-is
            # The linking will be handled by the effect parser
            return conditional
    
    return None


def _link_sequenced_effect(
    sentences: List[Sentence],
    index: int,
    ctx: ParseContext
) -> Optional[Effect]:
    """
    Link "Then" clause to previous effect.
    
    "Then" indicates strict sequencing - effects happen in order.
    
    Args:
        sentences: List of all sentences
        index: Index of the "Then" sentence
        ctx: ParseContext
        
    Returns:
        Effect if successfully parsed, None otherwise
    """
    if index == 0:
        return None  # No previous sentence
    
    current = sentences[index]
    
    # Check if current sentence is "Then"
    if current.continuation_type != "then":
        return None
    
    # Parse the effect from the current sentence
    effects = parse_effect_text(current.text, ctx)
    
    if effects:
        # For sequencing, we return the effects as-is
        # The sequencing will be handled by the effect parser or engine
        return effects[0] if len(effects) == 1 else None
    
    return None


def reconstruct_effect_chain(
    sentences: List[Sentence],
    ctx: ParseContext
) -> List[Effect]:
    """
    Reconstruct effect chain from sentences.
    
    Handles conditional effects, sequencing, and pronoun references.
    
    Args:
        sentences: List of Sentence objects from an ability chunk
        ctx: ParseContext for parsing
        
    Returns:
        List of Effect objects representing the reconstructed chain
    """
    if not sentences:
        return []
    
    effects: List[Effect] = []
    
    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        
        # Resolve pronoun references
        resolved_text = _resolve_pronoun_reference(
            sentence.text,
            sentences[:i],
            ctx
        )
        
        # Check for conditional effects
        if sentence.continuation_type == "if_you_do":
            conditional = _link_conditional_effect(sentences, i, ctx)
            if conditional:
                effects.append(conditional)
                i += 1
                continue
        
        # Check for sequenced effects ("Then")
        if sentence.continuation_type == "then":
            sequenced = _link_sequenced_effect(sentences, i, ctx)
            if sequenced:
                effects.append(sequenced)
                i += 1
                continue
        
        # Check for "As long as" conditionals
        if sentence.continuation_type == "as_long_as":
            # "As long as" introduces a conditional continuous effect
            # Parse it as a continuous effect with condition
            resolved_effects = parse_effect_text(resolved_text, ctx)
            effects.extend(resolved_effects)
            i += 1
            continue
        
        # Default: parse as regular effects
        resolved_effects = parse_effect_text(resolved_text, ctx)
        effects.extend(resolved_effects)
        
        i += 1
    
    return effects

