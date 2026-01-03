"""
Mana ability detection and marking.

Mana abilities are special activated abilities that produce mana.
They have different rules: they don't use the stack and can't be responded to.
"""

from axis2.schema import ActivatedAbility
from axis2.parsing.ability_detection import is_mana_ability


def mark_mana_abilities(activated_abilities: list[ActivatedAbility]) -> None:
    """
    Mark activated abilities as mana abilities if they produce mana.
    
    Modifies the abilities in place by setting is_mana_ability flag.
    
    Args:
        activated_abilities: List of activated abilities to check and mark
    """
    for ability in activated_abilities:
        if is_mana_producing_ability(ability):
            ability.is_mana_ability = True


def is_mana_producing_ability(ability: ActivatedAbility) -> bool:
    """
    Check if an activated ability produces mana.
    
    Args:
        ability: The activated ability to check
        
    Returns:
        True if the ability produces mana
    """
    # Check effects for mana production
    # This is a simplified check - in reality, we'd need to examine
    # the effect objects more carefully
    for effect in ability.effects:
        # Skip replacement effects - they don't produce mana
        from axis2.schema import ReplacementEffect
        if isinstance(effect, ReplacementEffect):
            continue
        
        # Check if effect is AddManaEffect or similar
        from axis2.schema import AddManaEffect
        if isinstance(effect, AddManaEffect):
            return True
        
        # Check effect text if available
        if hasattr(effect, 'text') and effect.text is not None:
            from axis2.parsing.ability_detection import is_mana_ability
            if is_mana_ability(effect.text):
                return True
    
    return False

