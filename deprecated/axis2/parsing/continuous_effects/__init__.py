# axis2/parsing/continuous_effects/__init__.py

"""
Backward-compatible API for continuous effects parsing.
Old code can still import parse_continuous_effects from here.
"""
from .dispatcher import parse_continuous_effects
from .base import ParseResult, ContinuousEffectParser
from .registry import register_parser, get_registry

# Explicit registration of all parsers
def _register_all_parsers():
    """
    Explicitly register all parsers in priority order.
    This gives us full control over registration and makes dependencies clear.
    """
    from . import pt_mod, abilities, ability_grant, color_change, type_change, protection, rule_change, loss_effects, cant_be_blocked, activation_restriction
    
    # Register in priority order (high to low)
    # P/T modifications first (most common)
    register_parser(pt_mod.PTParser())              # priority 60
    register_parser(pt_mod.BasePTParser())           # priority 55
    
    # Ability granting - comprehensive parser first (more specific patterns)
    register_parser(ability_grant.AbilityGrantParser())  # priority 50
    register_parser(abilities.AbilitiesParser())     # priority 50 (fallback)
    
    # Color changes
    register_parser(color_change.ColorChangeParser()) # priority 45
    
    # Type changes
    register_parser(type_change.TypeRemovalParser()) # priority 45 - must come before TypeChangeParser
    register_parser(type_change.TypeChangeParser())  # priority 40
    
    # Protection
    register_parser(protection.ProtectionParser())   # priority 35
    
    # Activation restrictions
    register_parser(activation_restriction.ActivationRestrictionParser()) # priority 35
    
    # Rule changes
    register_parser(rule_change.RuleChangeParser())  # priority 30
    
    # Loss effects
    register_parser(loss_effects.LossEffectsParser()) # priority 25
    
    # Can't be blocked
    register_parser(cant_be_blocked.CantBeBlockedParser()) # priority 20

_register_all_parsers()

__all__ = ['parse_continuous_effects', 'ParseResult', 'ContinuousEffectParser', 'register_parser']

