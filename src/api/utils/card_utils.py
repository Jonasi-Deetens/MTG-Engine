# src/api/utils/card_utils.py

"""Shared utilities for card conversion."""

from db.models import Axis1CardModel
from api.schemas.card_schemas import CardResponse


def _reconstruct_type_line(face: dict) -> str:
    """Reconstruct type_line from card_types, supertypes, and subtypes."""
    card_types = face.get("card_types", [])
    supertypes = face.get("supertypes", [])
    subtypes = face.get("subtypes", [])
    
    if not card_types:
        return ""
    
    # Build type line: supertypes + card_types + "—" + subtypes
    # Note: supertypes are a subset of card_types, so we need to preserve order
    # Format: "Basic Land — Forest" or "Creature — Human Wizard" or "Instant"
    
    # Start with all card_types (which includes supertypes in order)
    type_parts = list(card_types)
    
    # Combine types
    type_line = " ".join(type_parts)
    
    # Add subtypes if present (using em dash)
    if subtypes:
        type_line += " — " + " ".join(subtypes)
    
    return type_line


def card_model_to_response(card_model: Axis1CardModel) -> CardResponse:
    """Convert Axis1CardModel to CardResponse."""
    card_data = card_model.axis1_json or {}
    faces = card_data.get("faces", [])
    first_face = faces[0] if faces else {}
    characteristics = card_data.get("characteristics", {})
    metadata = card_data.get("metadata", {})
    
    # For multi-face cards, Scryfall provides image_uris per face
    # For single-face cards, image_uris are at the card level
    # We also check metadata as a fallback
    image_uris = (
        first_face.get("image_uris") or 
        card_data.get("image_uris") or 
        metadata.get("image_uris")
    )
    
    # Try to get type_line from face, or reconstruct it
    type_line = (
        first_face.get("type_line") or 
        card_data.get("type_line") or
        _reconstruct_type_line(first_face) or
        _reconstruct_type_line(characteristics)
    )
    
    return CardResponse(
        card_id=card_model.card_id,
        oracle_id=card_data.get("oracle_id"),
        name=first_face.get("name") or card_data.get("name", ""),
        mana_cost=first_face.get("mana_cost") or card_data.get("mana_cost"),
        mana_value=first_face.get("mana_value") or card_data.get("mana_value"),
        type_line=type_line,
        oracle_text=first_face.get("oracle_text") or card_data.get("oracle_text"),
        power=first_face.get("power") or card_data.get("power"),
        toughness=first_face.get("toughness") or card_data.get("toughness"),
        colors=first_face.get("colors", []) or card_data.get("colors", []),
        image_uris=image_uris,
        set_code=card_model.set_code,
        collector_number=card_model.collector_number,
        rarity=metadata.get("rarity"),
        legalities=metadata.get("legalities"),
        prices=metadata.get("prices"),
        artist=metadata.get("artist"),
        flavor_text=first_face.get("flavor_text") or card_data.get("flavor_text")
    )

