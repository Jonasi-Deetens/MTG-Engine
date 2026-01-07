# src/api/utils/deck_validator.py

"""Deck format validation utilities."""

from typing import List, Dict, Tuple
from api.schemas.deck_schemas import ValidationError, DeckValidationResponse


# Basic land names for Commander singleton exception
BASIC_LANDS = {
    "Plains", "Island", "Swamp", "Mountain", "Forest",
    "Snow-Covered Plains", "Snow-Covered Island", "Snow-Covered Swamp",
    "Snow-Covered Mountain", "Snow-Covered Forest"
}


def is_basic_land(card_name: str) -> bool:
    """Check if a card is a basic land."""
    return card_name in BASIC_LANDS


def validate_commander(
    card_count: int,
    commander_count: int,
    card_quantities: Dict[str, int],
    card_names: Dict[str, str]
) -> Tuple[List[ValidationError], List[ValidationError]]:
    """Validate Commander format rules."""
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    
    # Commander count validation
    if commander_count == 0:
        errors.append(ValidationError(
            type="error",
            message="Commander format requires at least 1 commander",
            field="commanders"
        ))
    elif commander_count > 2:
        errors.append(ValidationError(
            type="error",
            message="Commander format allows maximum 2 commanders (partner)",
            field="commanders"
        ))
    
    # Deck size validation
    if card_count != 100:
        errors.append(ValidationError(
            type="error",
            message=f"Commander format requires exactly 100 cards, found {card_count}",
            field="card_count"
        ))
    
    # Singleton rule validation
    for card_id, quantity in card_quantities.items():
        card_name = card_names.get(card_id, "")
        if quantity > 1 and not is_basic_land(card_name):
            errors.append(ValidationError(
                type="error",
                message=f"Commander format is singleton (max 1 copy). Found {quantity} copies of {card_name}",
                field=f"card_{card_id}"
            ))
    
    return errors, warnings


def validate_standard(
    card_count: int,
    card_quantities: Dict[str, int]
) -> Tuple[List[ValidationError], List[ValidationError]]:
    """Validate Standard format rules."""
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    
    if card_count < 60:
        errors.append(ValidationError(
            type="error",
            message=f"Standard format requires minimum 60 cards, found {card_count}",
            field="card_count"
        ))
    
    # Check for max 4 copies
    for card_id, quantity in card_quantities.items():
        if quantity > 4:
            errors.append(ValidationError(
                type="error",
                message=f"Standard format allows maximum 4 copies of a card. Found {quantity} copies",
                field=f"card_{card_id}"
            ))
    
    return errors, warnings


def validate_modern(
    card_count: int,
    card_quantities: Dict[str, int]
) -> Tuple[List[ValidationError], List[ValidationError]]:
    """Validate Modern format rules."""
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    
    if card_count < 60:
        errors.append(ValidationError(
            type="error",
            message=f"Modern format requires minimum 60 cards, found {card_count}",
            field="card_count"
        ))
    
    # Check for max 4 copies
    for card_id, quantity in card_quantities.items():
        if quantity > 4:
            errors.append(ValidationError(
                type="error",
                message=f"Modern format allows maximum 4 copies of a card. Found {quantity} copies",
                field=f"card_{card_id}"
            ))
    
    # Note: Card legality checking would require set information
    # This is a simplified version
    
    return errors, warnings


def validate_pauper(
    card_count: int,
    card_quantities: Dict[str, int],
    card_rarities: Dict[str, str]
) -> Tuple[List[ValidationError], List[ValidationError]]:
    """Validate Pauper format rules."""
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    
    if card_count < 60:
        errors.append(ValidationError(
            type="error",
            message=f"Pauper format requires minimum 60 cards, found {card_count}",
            field="card_count"
        ))
    
    # Check for max 4 copies
    for card_id, quantity in card_quantities.items():
        if quantity > 4:
            errors.append(ValidationError(
                type="error",
                message=f"Pauper format allows maximum 4 copies of a card. Found {quantity} copies",
                field=f"card_{card_id}"
            ))
    
    # Check rarity (all cards must be common)
    for card_id, rarity in card_rarities.items():
        if rarity and rarity.lower() != "common":
            errors.append(ValidationError(
                type="error",
                message=f"Pauper format only allows common rarity cards. Found {rarity}",
                field=f"card_{card_id}"
            ))
    
    return errors, warnings


def validate_legacy_vintage(
    card_count: int,
    card_quantities: Dict[str, int]
) -> Tuple[List[ValidationError], List[ValidationError]]:
    """Validate Legacy/Vintage format rules."""
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    
    if card_count < 60:
        errors.append(ValidationError(
            type="error",
            message=f"Format requires minimum 60 cards, found {card_count}",
            field="card_count"
        ))
    
    # Check for max 4 copies
    for card_id, quantity in card_quantities.items():
        if quantity > 4:
            errors.append(ValidationError(
                type="error",
                message=f"Format allows maximum 4 copies of a card. Found {quantity} copies",
                field=f"card_{card_id}"
            ))
    
    return errors, warnings


def validate_deck(
    format_type: str,
    card_count: int,
    commander_count: int,
    card_quantities: Dict[str, int],
    card_names: Dict[str, str] = None,
    card_rarities: Dict[str, str] = None
) -> DeckValidationResponse:
    """
    Validate a deck against format-specific rules.
    
    Args:
        format_type: The format (Commander, Standard, Modern, etc.)
        card_count: Total number of cards in deck
        commander_count: Number of commanders
        card_quantities: Dict mapping card_id to quantity
        card_names: Dict mapping card_id to card name (for basic land check)
        card_rarities: Dict mapping card_id to rarity (for Pauper)
    
    Returns:
        DeckValidationResponse with validation results
    """
    if card_names is None:
        card_names = {}
    if card_rarities is None:
        card_rarities = {}
    
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    
    format_lower = format_type.lower()
    
    if format_lower == "commander":
        format_errors, format_warnings = validate_commander(
            card_count, commander_count, card_quantities, card_names
        )
        errors.extend(format_errors)
        warnings.extend(format_warnings)
    elif format_lower == "standard":
        format_errors, format_warnings = validate_standard(card_count, card_quantities)
        errors.extend(format_errors)
        warnings.extend(format_warnings)
    elif format_lower == "modern":
        format_errors, format_warnings = validate_modern(card_count, card_quantities)
        errors.extend(format_errors)
        warnings.extend(format_warnings)
    elif format_lower == "pauper":
        format_errors, format_warnings = validate_pauper(
            card_count, card_quantities, card_rarities
        )
        errors.extend(format_errors)
        warnings.extend(format_warnings)
    elif format_lower in ["legacy", "vintage"]:
        format_errors, format_warnings = validate_legacy_vintage(card_count, card_quantities)
        errors.extend(format_errors)
        warnings.extend(format_warnings)
    else:
        # Generic validation for unknown formats
        if card_count < 60:
            warnings.append(ValidationError(
                type="warning",
                message=f"Deck has {card_count} cards. Most formats require at least 60.",
                field="card_count"
            ))
    
    return DeckValidationResponse(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        card_count=card_count,
        commander_count=commander_count,
        format=format_type
    )

