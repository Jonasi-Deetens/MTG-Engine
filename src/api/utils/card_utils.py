# src/api/utils/card_utils.py

"""Shared utilities for card conversion."""

from db.models import Axis1CardModel
from api.schemas.card_schemas import CardResponse


def card_model_to_response(card_model: Axis1CardModel) -> CardResponse:
    """Convert Axis1CardModel to CardResponse."""
    card_data = card_model.axis1_json or {}
    faces = card_data.get("faces", [])
    first_face = faces[0] if faces else {}
    metadata = card_data.get("metadata", {})
    
    # For multi-face cards, Scryfall provides image_uris per face
    # For single-face cards, image_uris are at the card level
    # We also check metadata as a fallback
    image_uris = (
        first_face.get("image_uris") or 
        card_data.get("image_uris") or 
        metadata.get("image_uris")
    )
    
    return CardResponse(
        card_id=card_model.card_id,
        oracle_id=card_data.get("oracle_id"),
        name=first_face.get("name") or card_data.get("name", ""),
        mana_cost=first_face.get("mana_cost") or card_data.get("mana_cost"),
        mana_value=first_face.get("mana_value") or card_data.get("mana_value"),
        type_line=first_face.get("type_line") or card_data.get("type_line"),
        oracle_text=first_face.get("oracle_text") or card_data.get("oracle_text"),
        power=first_face.get("power") or card_data.get("power"),
        toughness=first_face.get("toughness") or card_data.get("toughness"),
        colors=first_face.get("colors", []) or card_data.get("colors", []),
        image_uris=image_uris,
        set_code=card_model.set_code,
        collector_number=card_model.collector_number
    )

