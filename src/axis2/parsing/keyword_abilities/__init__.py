# axis2/parsing/keyword_abilities/__init__.py

from typing import List
from .registry import KeywordAbilityRegistry, KEYWORD_ALIASES
from .base import KeywordAbilityParser

_registry = None

def get_registry() -> KeywordAbilityRegistry:
    """Get the global keyword ability registry"""
    global _registry
    if _registry is None:
        _registry = KeywordAbilityRegistry()
    return _registry

def parse_keyword_abilities(text: str, ctx) -> tuple[List[str], List]:
    """
    Parse keyword abilities from text.
    
    Returns:
        Tuple of (keyword_names, effects) where:
        - keyword_names: List of keyword names found
        - effects: List of Effect objects parsed from keywords
    """
    registry = get_registry()
    keywords = []
    effects = []
    
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        result = registry.detect_keyword(line)
        if result:
            keyword_name, reminder_text, cost_text = result
            keywords.append(keyword_name)
            
            parsed_effects = registry.parse_keyword(
                keyword_name, reminder_text, cost_text, line, ctx
            )
            effects.extend(parsed_effects)
    
    return keywords, effects

__all__ = ['KeywordAbilityRegistry', 'KeywordAbilityParser', 'get_registry', 'parse_keyword_abilities', 'KEYWORD_ALIASES']

