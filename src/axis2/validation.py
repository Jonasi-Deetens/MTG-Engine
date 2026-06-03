"""
Validation functions for Axis2 schema objects.

This module provides validation functions to ensure parsed objects
are well-formed and valid according to MTG rules.
"""

from typing import List, Optional, Dict, Any
from axis2.schema import (
    Effect, ContinuousEffect, StaticEffect, ReplacementEffect,
    ActivatedAbility, TriggeredAbility, DealDamageEffect,
    DrawCardsEffect, AddManaEffect, CreateTokenEffect,
    SearchEffect, PutOntoBattlefieldEffect, ChangeZoneEffect,
    Subject, ManaCost, TargetingRules, Axis2Card, Axis2Face
)

# Valid zone names in MTG
VALID_ZONES = {
    "battlefield", "hand", "library", "graveyard", "exile",
    "stack", "command", "sideboard"
}

# Valid subject scopes
VALID_SCOPES = {
    "target", "each", "any_number", "up_to_n", "all", "self", "linked_exiled_card", "searched_card"
}

# Valid controller values
VALID_CONTROLLERS = {
    "you", "opponent", "any", "opponents", "controller", "owner"
}


def validate_damage_amount(amount: Any) -> List[str]:
    """
    Validate damage amount is positive.
    
    Args:
        amount: Damage amount (int or SymbolicValue)
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if isinstance(amount, int):
        if amount <= 0:
            errors.append(f"Damage amount must be positive, got {amount}")
    elif isinstance(amount, dict) and amount.get("kind") == "symbolic":
        # Symbolic values are always valid (X, *, etc.)
        pass
    else:
        errors.append(f"Invalid damage amount type: {type(amount)}")
    return errors


def validate_zone_name(zone: str) -> List[str]:
    """
    Validate zone name is valid.
    
    Args:
        zone: Zone name to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if zone not in VALID_ZONES:
        errors.append(f"Invalid zone name: {zone}. Valid zones: {VALID_ZONES}")
    return errors


def validate_subject_scope(scope: Optional[str]) -> List[str]:
    """
    Validate subject scope is valid.
    
    Args:
        scope: Scope to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if scope is not None and scope not in VALID_SCOPES:
        errors.append(f"Invalid scope: {scope}. Valid scopes: {VALID_SCOPES}")
    return errors


def validate_controller(controller: Optional[str]) -> List[str]:
    """
    Validate controller value is valid.
    
    Args:
        controller: Controller to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if controller is not None and controller not in VALID_CONTROLLERS:
        errors.append(f"Invalid controller: {controller}. Valid controllers: {VALID_CONTROLLERS}")
    return errors


def validate_mana_cost(mana_cost: Optional[ManaCost]) -> List[str]:
    """
    Validate mana cost is well-formed.
    
    Args:
        mana_cost: ManaCost to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if mana_cost is None:
        return errors  # None is valid
    
    if not isinstance(mana_cost, ManaCost):
        errors.append(f"Invalid mana cost type: {type(mana_cost)}")
        return errors
    
    if not isinstance(mana_cost.symbols, list):
        errors.append("ManaCost.symbols must be a list")
        return errors
    
    # Validate symbol format (basic check)
    valid_symbol_patterns = ["{", "}"]
    for symbol in mana_cost.symbols:
        if not isinstance(symbol, str):
            errors.append(f"Invalid symbol type: {type(symbol)}")
        elif not (symbol.startswith("{") and symbol.endswith("}")):
            errors.append(f"Invalid symbol format: {symbol}")
    
    return errors


def validate_subject(subject: Optional[Subject]) -> List[str]:
    """
    Validate Subject object.
    
    Args:
        subject: Subject to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if subject is None:
        return errors  # None is valid
    
    if not isinstance(subject, Subject):
        errors.append(f"Invalid subject type: {type(subject)}")
        return errors
    
    errors.extend(validate_subject_scope(subject.scope))
    errors.extend(validate_controller(subject.controller))
    
    return errors


def validate_deal_damage_effect(effect: DealDamageEffect) -> List[str]:
    """
    Validate DealDamageEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    errors.extend(validate_damage_amount(effect.amount))
    errors.extend(validate_subject(effect.subject))
    return errors


def validate_draw_cards_effect(effect: DrawCardsEffect) -> List[str]:
    """
    Validate DrawCardsEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if isinstance(effect.amount, int) and effect.amount <= 0:
        errors.append(f"Draw amount must be positive, got {effect.amount}")
    return errors


def validate_add_mana_effect(effect: AddManaEffect) -> List[str]:
    """
    Validate AddManaEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if not isinstance(effect.mana, list) or len(effect.mana) == 0:
        errors.append("AddManaEffect.mana must be a non-empty list")
    else:
        # Special values allowed when choice is set (e.g., "any_color" for choice="color")
        special_values = {"any_color", "any_type"}
        for symbol in effect.mana:
            if not isinstance(symbol, str):
                errors.append(f"Invalid mana symbol type: {type(symbol)}")
            elif symbol in special_values:
                # Allow special values when choice is set
                if effect.choice is None:
                    errors.append(f"Special mana value '{symbol}' requires choice to be set")
            elif not (symbol.startswith("{") and symbol.endswith("}")):
                errors.append(f"Invalid mana symbol format: {symbol}")
    return errors


def validate_search_effect(effect: SearchEffect) -> List[str]:
    """
    Validate SearchEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if not isinstance(effect.zones, list) or len(effect.zones) == 0:
        errors.append("SearchEffect.zones must be a non-empty list")
    else:
        for zone in effect.zones:
            errors.extend(validate_zone_name(zone))
    
    if effect.max_results is not None and isinstance(effect.max_results, int):
        if effect.max_results <= 0:
            errors.append(f"SearchEffect.max_results must be positive, got {effect.max_results}")
    
    return errors


def validate_put_onto_battlefield_effect(effect: PutOntoBattlefieldEffect) -> List[str]:
    """
    Validate PutOntoBattlefieldEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    errors.extend(validate_zone_name(effect.zone_from))
    
    if not isinstance(effect.card_filter, dict):
        errors.append("PutOntoBattlefieldEffect.card_filter must be a dict")
    
    return errors


def validate_change_zone_effect(effect: ChangeZoneEffect) -> List[str]:
    """
    Validate ChangeZoneEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if effect.from_zone is not None:
        errors.extend(validate_zone_name(effect.from_zone))
    if effect.to_zone is not None:
        errors.extend(validate_zone_name(effect.to_zone))
    errors.extend(validate_subject(effect.subject))
    return errors


def validate_continuous_effect(effect: ContinuousEffect) -> List[str]:
    """
    Validate ContinuousEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate layer is in valid range (1-7)
    if not isinstance(effect.layer, int) or effect.layer < 1 or effect.layer > 7:
        errors.append(f"ContinuousEffect.layer must be 1-7, got {effect.layer}")
    
    # Validate sublayer format if present
    if effect.sublayer is not None:
        if not isinstance(effect.sublayer, str):
            errors.append(f"ContinuousEffect.sublayer must be a string, got {type(effect.sublayer)}")
        elif not effect.sublayer.startswith(str(effect.layer)):
            errors.append(f"ContinuousEffect.sublayer {effect.sublayer} doesn't match layer {effect.layer}")
    
    # Validate applies_to if it's a Subject
    if isinstance(effect.applies_to, Subject):
        errors.extend(validate_subject(effect.applies_to))
    
    return errors


def validate_static_effect(effect: StaticEffect) -> List[str]:
    """
    Validate StaticEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate layer is in valid range (1-7)
    if not isinstance(effect.layer, int) or effect.layer < 1 or effect.layer > 7:
        errors.append(f"StaticEffect.layer must be 1-7, got {effect.layer}")
    
    # Validate zones
    if not isinstance(effect.zones, list) or len(effect.zones) == 0:
        errors.append("StaticEffect.zones must be a non-empty list")
    else:
        for zone in effect.zones:
            errors.extend(validate_zone_name(zone))
    
    # Validate subject
    errors.extend(validate_subject(effect.subject))
    
    return errors


def validate_replacement_effect(effect: ReplacementEffect) -> List[str]:
    """
    Validate ReplacementEffect.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate zones
    if not isinstance(effect.zones, list) or len(effect.zones) == 0:
        errors.append("ReplacementEffect.zones must be a non-empty list")
    else:
        for zone in effect.zones:
            errors.extend(validate_zone_name(zone))
    
    # Validate subject
    errors.extend(validate_subject(effect.subject))
    
    return errors


def validate_activated_ability(ability: ActivatedAbility) -> List[str]:
    """
    Validate ActivatedAbility.
    
    Args:
        ability: Ability to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if not isinstance(ability.costs, list) or len(ability.costs) == 0:
        errors.append("ActivatedAbility.costs must be a non-empty list")
    
    if not isinstance(ability.effects, list) or len(ability.effects) == 0:
        errors.append("ActivatedAbility.effects must be a non-empty list")
    
    return errors


def validate_triggered_ability(ability: TriggeredAbility) -> List[str]:
    """
    Validate TriggeredAbility.
    
    Args:
        ability: Ability to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if not isinstance(ability.effects, list) or len(ability.effects) == 0:
        errors.append("TriggeredAbility.effects must be a non-empty list")
    
    if not ability.condition_text:
        errors.append("TriggeredAbility.condition_text must not be empty")
    
    return errors


def validate_axis2_face(face: Axis2Face) -> List[str]:
    """
    Validate Axis2Face.
    
    Args:
        face: Face to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate mana cost
    errors.extend(validate_mana_cost(face.mana_cost))
    
    # Validate all effects
    for effect in face.spell_effects:
        if isinstance(effect, DealDamageEffect):
            errors.extend(validate_deal_damage_effect(effect))
        elif isinstance(effect, DrawCardsEffect):
            errors.extend(validate_draw_cards_effect(effect))
        elif isinstance(effect, AddManaEffect):
            errors.extend(validate_add_mana_effect(effect))
        elif isinstance(effect, SearchEffect):
            errors.extend(validate_search_effect(effect))
        elif isinstance(effect, PutOntoBattlefieldEffect):
            errors.extend(validate_put_onto_battlefield_effect(effect))
        elif isinstance(effect, ChangeZoneEffect):
            errors.extend(validate_change_zone_effect(effect))
    
    # Validate continuous effects
    for effect in face.continuous_effects:
        errors.extend(validate_continuous_effect(effect))
    
    # Validate static effects
    for effect in face.static_effects:
        errors.extend(validate_static_effect(effect))
    
    # Validate replacement effects
    for effect in face.replacement_effects:
        errors.extend(validate_replacement_effect(effect))
    
    # Validate activated abilities
    for ability in face.activated_abilities:
        errors.extend(validate_activated_ability(ability))
    
    # Validate triggered abilities
    for ability in face.triggered_abilities:
        errors.extend(validate_triggered_ability(ability))
    
    return errors


def validate_axis2_card(card: Axis2Card) -> List[str]:
    """
    Validate Axis2Card.
    
    Args:
        card: Card to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if not card.faces or len(card.faces) == 0:
        errors.append("Axis2Card must have at least one face")
    
    for face in card.faces:
        errors.extend(validate_axis2_face(face))
    
    return errors


def validate_effect(effect: Effect) -> List[str]:
    """
    Generic validator that dispatches to specific validators based on effect type.
    
    Args:
        effect: Effect to validate
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if isinstance(effect, DealDamageEffect):
        errors.extend(validate_deal_damage_effect(effect))
    elif isinstance(effect, DrawCardsEffect):
        errors.extend(validate_draw_cards_effect(effect))
    elif isinstance(effect, AddManaEffect):
        errors.extend(validate_add_mana_effect(effect))
    elif isinstance(effect, SearchEffect):
        errors.extend(validate_search_effect(effect))
    elif isinstance(effect, PutOntoBattlefieldEffect):
        errors.extend(validate_put_onto_battlefield_effect(effect))
    elif isinstance(effect, ChangeZoneEffect):
        errors.extend(validate_change_zone_effect(effect))
    elif isinstance(effect, ContinuousEffect):
        errors.extend(validate_continuous_effect(effect))
    elif isinstance(effect, StaticEffect):
        errors.extend(validate_static_effect(effect))
    elif isinstance(effect, ReplacementEffect):
        errors.extend(validate_replacement_effect(effect))
    # Add more effect types as needed
    
    return errors

