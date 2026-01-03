# axis2/parsing/replacement_effects/__init__.py

"""
Backward-compatible API for replacement effects parsing.
Old code can still import parse_replacement_effects from here.
"""
from .dispatcher import parse_replacement_effects
from .base import ParseResult, ReplacementEffectParser
from .registry import register_parser, get_registry

# Explicit registration of all parsers
def _register_all_parsers():
    """
    Explicitly register all parsers in priority order.
    This gives us full control over registration and makes dependencies clear.
    """
    from . import delayed, zone_change, dies, enter_tapped, damage, draw, mana_replacement, counter_modification
    
    # Register in priority order (high to low)
    register_parser(mana_replacement.ManaReplacementParser())  # priority 60
    register_parser(delayed.DelayedParser())          # priority 55
    register_parser(counter_modification.CounterModificationParser())  # priority 50
    register_parser(zone_change.ZoneChangeParser())   # priority 50
    register_parser(dies.DiesParser())                 # priority 45
    register_parser(enter_tapped.EnterTappedParser())  # priority 40
    register_parser(damage.DamageParser())            # priority 35
    register_parser(draw.DrawParser())                 # priority 30

_register_all_parsers()

__all__ = ['parse_replacement_effects', 'ParseResult', 'ReplacementEffectParser', 'register_parser']

