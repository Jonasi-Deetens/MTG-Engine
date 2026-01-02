# axis2/parsing/static_effects/__init__.py

"""
Backward-compatible API for static effects parsing.
Old code can still import parse_static_effects from here.
"""
from .dispatcher import parse_static_effects, parse_general_static_effects
from .base import ParseResult, StaticEffectParser
from .registry import register_parser, get_registry

# Explicit registration of all parsers
def _register_all_parsers():
    """
    Explicitly register all parsers in priority order.
    This gives us full control over registration and makes dependencies clear.
    """
    from . import blocking, crew_power, haste, top_reveal, zone_addition, cost_modification
    
    # Register in priority order (high to low)
    register_parser(blocking.BlockingParser())              # priority 50
    register_parser(crew_power.CrewPowerParser())           # priority 45
    register_parser(haste.HasteParser())                    # priority 40
    register_parser(top_reveal.TopRevealParser())           # priority 35
    register_parser(zone_addition.ZoneAdditionParser())     # priority 30
    register_parser(cost_modification.CostModificationParser()) # priority 25

_register_all_parsers()

__all__ = ['parse_static_effects', 'parse_general_static_effects', 'ParseResult', 'StaticEffectParser', 'register_parser']

