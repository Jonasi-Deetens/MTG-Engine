# axis2/parsing/effects/dispatcher.py

from typing import List
from .base import ParseResult
from .registry import get_registry
from .utils import split_effect_sentences
from axis2.schema import Effect, ParseContext, AddManaEffect
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
    
    # Get registry once
    registry = get_registry()
    
    # Check for conditional mana replacement before splitting
    # This handles patterns like "Add {C}. If condition, add {C}{C} instead"
    conditional_mana_result = registry.parse(text, ctx)
    if conditional_mana_result.is_success:
        effects = conditional_mana_result.all_effects
        if effects:
            effect = effects[0]
            # Check if it's a conditional mana effect with both base and replacement
            if isinstance(effect, AddManaEffect) and effect.condition and effect.replacement_mana and effect.mana:
                return [effect]  # Return the combined effect
    
    # Split into sentences
    sentences = split_effect_sentences(text)
    
    # Special-case global effects that span sentences.
    # TODO: This should eventually become a parser-level concern.
    # For now, we handle look-and-pick effects that need the full text
    # before sentence splitting. This is technical debt, not architecture.
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
        print(f"[DEBUG Dispatcher] Parsing sentence: '{s}'")
        candidates = registry._find_candidates(s, ctx)
        print(f"[DEBUG Dispatcher] Found {len(candidates)} candidate parsers: {[type(p).__name__ for p in candidates[:5]]}")
        result = registry.parse(s, ctx)
        print(f"[DEBUG Dispatcher] Parse result: matched={result.matched}, is_success={result.is_success}, errors={result.errors}, effects={result.all_effects}")
        if result.is_success:
            print(f"[DEBUG Dispatcher] Successfully parsed '{s}' -> {len(result.all_effects)} effects")
            effects.extend(result.all_effects)
        else:
            print(f"[DEBUG Dispatcher] Failed to parse: {s[:50]}... matched={result.matched}, errors={result.errors}")
            if result.errors:
                print(f"[DEBUG Dispatcher] Errors: {result.errors}")
            print(f"[DEBUG Dispatcher] Tried parsers: {[type(p).__name__ for p in candidates[:3]]}")
    
    return effects

