"""
Backward-compatible API for effects parsing.
Old code can still import parse_effect_text from here.
"""
from .dispatcher import parse_effect_text
from .base import ParseResult, EffectParser
from .registry import register_parser, get_registry

# Explicit registration of all parsers
def _register_all_parsers():
    """
    Explicitly register all parsers in priority order.
    This gives us full control over registration and makes dependencies clear.
    """
    from . import damage, search, tokens, zone_changes, counters, life, draw, mana, look_pick, protection, misc, casting_permission, discard, conditional_mana
    
    # Register in priority order (high to low)
    # Very specific patterns first
    register_parser(conditional_mana.ConditionalManaParser())  # priority 70 - must come before ManaParser
    register_parser(search.LightpawsSearchParser())  # priority 100
    register_parser(look_pick.LookAndPickParser())   # priority 90
    register_parser(search.SearchParser())            # priority 80
    register_parser(casting_permission.CastingPermissionParser())  # priority 60
    
    # Common effects
    register_parser(tokens.TokenParser())             # priority 60
    register_parser(damage.DamageParser())            # priority 50
    register_parser(counters.CounterParser())         # priority 50
    register_parser(life.LifeParser())                # priority 50
    register_parser(misc.CounterSpellParser())        # priority 50
    register_parser(misc.PTBoostParser())             # priority 50
    register_parser(discard.DiscardParser())          # priority 50
    
    # Generic effects
    register_parser(zone_changes.ZoneChangeParser())  # priority 40
    register_parser(misc.ReturnCardParser())          # priority 40
    register_parser(draw.DrawParser())                # priority 30
    register_parser(mana.ManaParser())                # priority 30
    register_parser(protection.ProtectionParser())     # priority 30
    register_parser(misc.ScryParser())                # priority 30
    register_parser(misc.SurveilParser())             # priority 30
    register_parser(misc.RevealThoseParser())          # priority 30
    register_parser(misc.SpellbookParser())           # priority 30
    register_parser(misc.EquipParser())               # priority 30
    
    # Low priority generic effects
    register_parser(misc.ShuffleParser())             # priority 20

_register_all_parsers()

__all__ = ['parse_effect_text', 'ParseResult', 'EffectParser', 'register_parser']

