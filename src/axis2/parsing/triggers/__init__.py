# axis2/parsing/triggers/__init__.py

"""
Backward-compatible API for trigger parsing.
Old code can still import parse_trigger_event and parse_spell_filter from here.
"""
from .dispatcher import parse_trigger_event
from .utils import parse_spell_filter
from .base import ParseResult, TriggerParser
from .registry import register_parser, get_registry

# Explicit registration of all parsers
def _register_all_parsers():
    """
    Explicitly register all parsers in priority order.
    This gives us full control over registration and makes dependencies clear.
    """
    from . import zone_change, damage, etb, ltb, cast_spell, attacks
    
    # Register in priority order (high to low)
    register_parser(zone_change.ZoneChangeParser())  # priority 50
    register_parser(damage.DamageParser())            # priority 45
    register_parser(etb.ETBParser())                  # priority 40
    register_parser(ltb.LTBParser())                  # priority 35
    register_parser(cast_spell.CastSpellParser())    # priority 30
    register_parser(attacks.AttacksParser())          # priority 25

_register_all_parsers()

__all__ = ['parse_trigger_event', 'parse_spell_filter', 'ParseResult', 'TriggerParser', 'register_parser']

