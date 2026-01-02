# axis2/parsing/effects/dispatcher.py

from typing import List
from .base import ParseResult
from .registry import get_registry
from .utils import split_effect_sentences
from axis2.schema import Effect, ParseContext
from axis2.parsing.conditional_effects import parse_conditional
from axis2.parsing.spell_continuous_effects import parse_spell_continuous_effect
import logging

logger = logging.getLogger(__name__)

def parse_effect_text(text: str, ctx: ParseContext) -> List[Effect]:
    """
    Main entry point - replaces the old parse_effect_text.
    Now uses registry pattern instead of hardcoded chain.
    
    ⚠️ RULE: This function MUST NEVER call itself recursively.
    If recursion is needed (e.g., parsing remainder after partial match),
    it belongs inside a specific parser with bounded depth.
    """
    if not text:
        return []
    
    # Add current text to context for diagnostics
    # This enables better error messages and test failures
    # NOTE: Requires ParseContext.current_effect_text field in schema
    # If ParseContext is immutable, create new context with this field set
    if hasattr(ctx, 'current_effect_text'):
        # Set current text for diagnostic purposes
        # (Would need to create new context if immutable)
        pass  # Implementation depends on ParseContext mutability
    
    # Check for conditional effects first (special case)
    cond = parse_conditional(text, ctx)
    if cond:
        return [cond]
    
    # Split into sentences
    sentences = split_effect_sentences(text)
    
    # Special-case global effects that span sentences.
    # TODO: This should eventually become a parser-level concern.
    # For now, we handle look-and-pick effects that need the full text
    # before sentence splitting. This is technical debt, not architecture.
    registry = get_registry()
    look_pick_result = registry.parse(text, ctx)
    if look_pick_result.is_success and "look at" in text.lower():
        effects = look_pick_result.all_effects
    else:
        effects = []
    
    # Determine if we should skip spell continuous effects
    skip_spell_continuous = ctx.is_static_ability or ctx.is_triggered_ability or not ctx.is_spell_text
    
    # Parse each sentence
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        
        # Try conditional first
        cond = parse_conditional(s, ctx)
        if cond:
            effects.append(cond)
            continue
        
        # Try spell continuous effects (special case with context flag)
        if not skip_spell_continuous:
            spell_continuous = parse_spell_continuous_effect(s, ctx)
            if spell_continuous:
                effects.append(spell_continuous)
                continue
        
        # Use registry to find matching parser
        result = registry.parse(s, ctx)
        if result.is_success:
            effects.extend(result.all_effects)
        else:
            logger.warning(f"Failed to parse: {s[:50]}...")
            if result.errors:
                logger.debug(f"Errors: {result.errors}")
    
    return effects

