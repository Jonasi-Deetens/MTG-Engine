# axis2/parsing/effects.py
"""
Backward-compatible API for effects parsing.
Old code can still import parse_effect_text from here.

This file is a re-export from the new effects/ package.
The actual implementation is in effects/dispatcher.py.
"""
from .effects.dispatcher import parse_effect_text
from .effects.base import ParseResult, EffectParser
from .effects.registry import register_parser, get_registry

__all__ = ['parse_effect_text', 'ParseResult', 'EffectParser', 'register_parser', 'get_registry']
