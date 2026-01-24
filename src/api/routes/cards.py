# src/api/routes/cards.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text
from typing import Optional, List, Dict, Any, Tuple

from db.connection import SessionLocal
from db.models import Axis1CardModel
from db.repository import Axis1Repository
from scryfall.client import ScryfallClient
from api.routes.auth import get_current_user, get_optional_user
from db.models import User
from api.schemas.card_schemas import CardResponse, SearchResponse
from api.utils.card_utils import card_model_to_response

router = APIRouter(prefix="/api/cards", tags=["cards"])
def _split_filter_list(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [entry.strip() for entry in raw.split(",") if entry.strip()]


def _apply_card_filters(
    query,
    *,
    q: Optional[str],
    colors: Optional[str],
    color_identity: Optional[str],
    types: Optional[str],
    supertypes: Optional[str],
    subtypes: Optional[str],
    keywords: Optional[str],
    rarity: Optional[str],
    set_code: Optional[str],
    layout: Optional[str],
    produced_mana: Optional[str],
    lang: Optional[str],
    cmc_min: Optional[float],
    cmc_max: Optional[float],
    power_min: Optional[int],
    power_max: Optional[int],
    toughness_min: Optional[int],
    toughness_max: Optional[int],
    loyalty_min: Optional[int],
    loyalty_max: Optional[int],
    is_legendary: Optional[bool],
) -> Tuple[Any, Dict[str, Any]]:
    params: Dict[str, Any] = {}
    search_index = "axis1_json->'search_index'"
    fallback_colors = f"COALESCE({search_index}->'colors', axis1_json->'faces'->0->'colors', axis1_json->'characteristics'->'colors')"
    fallback_color_identity = f"COALESCE({search_index}->'color_identity', axis1_json->'characteristics'->'color_identity')"
    fallback_card_types = f"COALESCE({search_index}->'card_types', axis1_json->'characteristics'->'card_types')"
    fallback_supertypes = f"COALESCE({search_index}->'supertypes', axis1_json->'characteristics'->'supertypes')"
    fallback_subtypes = f"COALESCE({search_index}->'subtypes', axis1_json->'characteristics'->'subtypes')"
    fallback_keywords = f"COALESCE({search_index}->'keywords', axis1_json->'faces'->0->'keywords')"
    fallback_produced = f"COALESCE({search_index}->'produced_mana', axis1_json->'faces'->0->'produced_mana')"
    fallback_type_line = f"COALESCE({search_index}->>'type_line', axis1_json->'faces'->0->>'type_line', axis1_json->>'type_line')"
    fallback_oracle_text = f"COALESCE({search_index}->>'oracle_text', axis1_json->'faces'->0->>'oracle_text', axis1_json->>'oracle_text')"
    fallback_name = f"COALESCE({search_index}->>'name', axis1_json->'faces'->0->>'name', axis1_json->>'name')"
    fallback_mana_value = f"COALESCE({search_index}->>'mana_value', axis1_json->'characteristics'->>'mana_value')"
    fallback_power = f"COALESCE({search_index}->>'power', axis1_json->'characteristics'->>'power')"
    fallback_toughness = f"COALESCE({search_index}->>'toughness', axis1_json->'characteristics'->>'toughness')"
    fallback_loyalty = f"COALESCE({search_index}->>'loyalty', axis1_json->'characteristics'->>'loyalty')"

    if q:
        params["q_like"] = f"%{q}%"
        query = query.filter(or_(
            text(f"LOWER({fallback_name}) LIKE LOWER(:q_like)"),
            text(f"LOWER({fallback_type_line}) LIKE LOWER(:q_like)"),
            text(f"LOWER({fallback_oracle_text}) LIKE LOWER(:q_like)"),
        ))

    if set_code:
        params["set_code_like"] = f"%{set_code}%"
        query = query.filter(text("LOWER(axis1_json->>'set') LIKE LOWER(:set_code_like)"))

    if rarity:
        params["rarity"] = rarity.lower()
        query = query.filter(text(f"LOWER({search_index}->>'rarity') = :rarity"))

    if layout:
        params["layout"] = layout.lower()
        query = query.filter(text(f"LOWER({search_index}->>'layout') = :layout"))

    if lang:
        params["lang"] = lang.lower()
        query = query.filter(
            or_(
                text("LOWER(lang) = :lang"),
                text("LOWER(axis1_json->>'lang') = :lang"),
            )
        )

    color_list = [c.upper() for c in _split_filter_list(colors) if c.upper() in {"W", "U", "B", "R", "G", "C"}]
    if color_list:
        color_conditions = []
        if "C" in color_list:
            color_conditions.append(text(
                f"{fallback_colors} IS NULL OR {fallback_colors} = '[]'::jsonb"
            ))
        for idx, color in enumerate([c for c in color_list if c != "C"]):
            key = f"color_{idx}"
            params[key] = f'["{color}"]'
            color_conditions.append(text(f"{fallback_colors} @> (:{key})::jsonb"))
        query = query.filter(or_(*color_conditions))

    identity_list = [c.upper() for c in _split_filter_list(color_identity) if c.upper() in {"W", "U", "B", "R", "G", "C"}]
    if identity_list:
        identity_conditions = []
        if "C" in identity_list:
            identity_conditions.append(text(
                f"{fallback_color_identity} IS NULL OR {fallback_color_identity} = '[]'::jsonb"
            ))
        for idx, color in enumerate([c for c in identity_list if c != "C"]):
            key = f"identity_{idx}"
            params[key] = f'["{color}"]'
            identity_conditions.append(text(f"{fallback_color_identity} @> (:{key})::jsonb"))
        query = query.filter(or_(*identity_conditions))

    type_list = _split_filter_list(types)
    if type_list:
        type_conditions = []
        for idx, value in enumerate(type_list):
            key = f"type_{idx}"
            like_key = f"type_like_{idx}"
            params[key] = f'["{value}"]'
            params[like_key] = f"%{value}%"
            # Check card_types array OR type_line string (case-insensitive)
            type_conditions.append(text(f"{fallback_card_types} @> (:{key})::jsonb"))
            type_conditions.append(text(f"LOWER({fallback_type_line}) LIKE LOWER(:{like_key})"))
        query = query.filter(or_(*type_conditions))

    super_list = _split_filter_list(supertypes)
    if super_list:
        super_conditions = []
        for idx, value in enumerate(super_list):
            key = f"super_{idx}"
            params[key] = f'["{value}"]'
            super_conditions.append(text(f"{fallback_supertypes} @> (:{key})::jsonb"))
        query = query.filter(or_(*super_conditions))

    sub_list = _split_filter_list(subtypes)
    if sub_list:
        sub_conditions = []
        for idx, value in enumerate(sub_list):
            key = f"sub_{idx}"
            params[key] = f'["{value}"]'
            sub_conditions.append(text(f"{fallback_subtypes} @> (:{key})::jsonb"))
        query = query.filter(or_(*sub_conditions))

    keyword_list = _split_filter_list(keywords)
    if keyword_list:
        keyword_conditions = []
        for idx, value in enumerate(keyword_list):
            key = f"keyword_{idx}"
            params[key] = f'["{value}"]'
            keyword_conditions.append(text(f"{fallback_keywords} @> (:{key})::jsonb"))
        query = query.filter(or_(*keyword_conditions))

    produced_list = [c.upper() for c in _split_filter_list(produced_mana) if c.upper() in {"W", "U", "B", "R", "G", "C"}]
    if produced_list:
        produced_conditions = []
        for idx, value in enumerate(produced_list):
            key = f"produced_{idx}"
            params[key] = f'["{value}"]'
            produced_conditions.append(text(f"{fallback_produced} @> (:{key})::jsonb"))
        query = query.filter(or_(*produced_conditions))

    if cmc_min is not None:
        params["cmc_min"] = cmc_min
        query = query.filter(text(f"CAST({fallback_mana_value} AS FLOAT) >= :cmc_min"))
    if cmc_max is not None:
        params["cmc_max"] = cmc_max
        query = query.filter(text(f"CAST({fallback_mana_value} AS FLOAT) <= :cmc_max"))

    def _numeric_filter(field: str, min_value: Optional[int], max_value: Optional[int], prefix: str) -> None:
        nonlocal query
        if min_value is not None:
            params[f"{prefix}_min"] = min_value
            query = query.filter(text(
                f"CASE WHEN ({fallback_power if field == 'power' else fallback_toughness if field == 'toughness' else fallback_loyalty}) ~ '^-?\\d+$' "
                f"THEN ({fallback_power if field == 'power' else fallback_toughness if field == 'toughness' else fallback_loyalty})::int ELSE NULL END >= :{prefix}_min"
            ))
        if max_value is not None:
            params[f"{prefix}_max"] = max_value
            query = query.filter(text(
                f"CASE WHEN ({fallback_power if field == 'power' else fallback_toughness if field == 'toughness' else fallback_loyalty}) ~ '^-?\\d+$' "
                f"THEN ({fallback_power if field == 'power' else fallback_toughness if field == 'toughness' else fallback_loyalty})::int ELSE NULL END <= :{prefix}_max"
            ))

    _numeric_filter("power", power_min, power_max, "power")
    _numeric_filter("toughness", toughness_min, toughness_max, "toughness")
    _numeric_filter("loyalty", loyalty_min, loyalty_max, "loyalty")

    if is_legendary is not None:
        if is_legendary:
            query = query.filter(text(f"{fallback_supertypes} @> '[\"Legendary\"]'::jsonb"))
        else:
            query = query.filter(text(f"NOT ({fallback_supertypes} @> '[\"Legendary\"]'::jsonb)"))

    return query, params



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/search", response_model=SearchResponse)
def search_cards(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    colors: Optional[str] = Query(None, description="Comma-separated color filter (e.g., 'W,U')"),
    color_identity: Optional[str] = Query(None, description="Comma-separated color identity filter"),
    types: Optional[str] = Query(None, description="Comma-separated card types filter"),
    supertypes: Optional[str] = Query(None, description="Comma-separated supertypes filter"),
    subtypes: Optional[str] = Query(None, description="Comma-separated subtypes filter"),
    keywords: Optional[str] = Query(None, description="Comma-separated keywords filter"),
    rarity: Optional[str] = Query(None, description="Rarity filter (common, uncommon, rare, mythic)"),
    set_code: Optional[str] = Query(None, description="Set code filter"),
    layout: Optional[str] = Query(None, description="Card layout filter"),
    produced_mana: Optional[str] = Query(None, description="Comma-separated produced mana colors"),
    lang: Optional[str] = Query(None, description="Language code filter (e.g., 'en', 'ja')"),
    cmc_min: Optional[float] = Query(None, description="Minimum mana value (cmc)"),
    cmc_max: Optional[float] = Query(None, description="Maximum mana value (cmc)"),
    power_min: Optional[int] = Query(None, description="Minimum power"),
    power_max: Optional[int] = Query(None, description="Maximum power"),
    toughness_min: Optional[int] = Query(None, description="Minimum toughness"),
    toughness_max: Optional[int] = Query(None, description="Maximum toughness"),
    loyalty_min: Optional[int] = Query(None, description="Minimum loyalty"),
    loyalty_max: Optional[int] = Query(None, description="Maximum loyalty"),
    is_legendary: Optional[bool] = Query(None, description="Filter for legendary cards"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    """Search cards in the database."""
    query = db.query(Axis1CardModel)

    query, params = _apply_card_filters(
        query,
        q=q,
        colors=colors,
        color_identity=color_identity,
        types=types,
        supertypes=supertypes,
        subtypes=subtypes,
        keywords=keywords,
        rarity=rarity,
        set_code=set_code,
        layout=layout,
        produced_mana=produced_mana,
        lang=lang,
        cmc_min=cmc_min,
        cmc_max=cmc_max,
        power_min=power_min,
        power_max=power_max,
        toughness_min=toughness_min,
        toughness_max=toughness_max,
        loyalty_min=loyalty_min,
        loyalty_max=loyalty_max,
        is_legendary=is_legendary,
    )
    if params:
        query = query.params(**params)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    cards = query.offset(offset).limit(page_size).all()
    
    # Convert to response models
    card_responses = [card_model_to_response(card) for card in cards]
    
    return SearchResponse(
        cards=card_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(cards)) < total
    )


@router.get("/random", response_model=CardResponse)
def get_random_card(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    """Get a random card from the database."""
    card = db.query(Axis1CardModel).order_by(func.random()).first()
    if not card:
        raise HTTPException(status_code=404, detail="No cards found")
    return card_model_to_response(card)


@router.get("/versions/{card_id}", response_model=List[CardResponse])
def get_card_versions(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all versions (printings) of a card by looking up the card's name."""
    # Get the card to find its name
    card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Use the name field from the model to find all versions
    card_name = card.name
    if not card_name:
        raise HTTPException(status_code=404, detail="Card name not found")
    
    # Find all cards with the same name
    all_versions = db.query(Axis1CardModel).filter(
        Axis1CardModel.name == card_name
    ).all()
    
    return [card_model_to_response(c) for c in all_versions]


@router.get("/{card_id}", response_model=CardResponse)
def get_card(
    card_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    """Get a card by ID."""
    card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return card_model_to_response(card)


@router.get("", response_model=SearchResponse)
def list_cards(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    colors: Optional[str] = Query(None, description="Comma-separated color filter (e.g., 'W,U' for white or blue)"),
    color_identity: Optional[str] = Query(None, description="Comma-separated color identity filter"),
    types: Optional[str] = Query(None, description="Comma-separated card types filter"),
    supertypes: Optional[str] = Query(None, description="Comma-separated supertypes filter"),
    subtypes: Optional[str] = Query(None, description="Comma-separated subtypes filter"),
    keywords: Optional[str] = Query(None, description="Comma-separated keywords filter"),
    rarity: Optional[str] = Query(None, description="Rarity filter (common, uncommon, rare, mythic)"),
    set_code: Optional[str] = Query(None, description="Set code filter"),
    layout: Optional[str] = Query(None, description="Card layout filter"),
    produced_mana: Optional[str] = Query(None, description="Comma-separated produced mana colors"),
    lang: Optional[str] = Query(None, description="Language code filter (e.g., 'en', 'ja')"),
    cmc_min: Optional[float] = Query(None, description="Minimum mana value (cmc)"),
    cmc_max: Optional[float] = Query(None, description="Maximum mana value (cmc)"),
    power_min: Optional[int] = Query(None, description="Minimum power"),
    power_max: Optional[int] = Query(None, description="Maximum power"),
    toughness_min: Optional[int] = Query(None, description="Minimum toughness"),
    toughness_max: Optional[int] = Query(None, description="Maximum toughness"),
    loyalty_min: Optional[int] = Query(None, description="Minimum loyalty"),
    loyalty_max: Optional[int] = Query(None, description="Maximum loyalty"),
    is_legendary: Optional[bool] = Query(None, description="Filter for legendary cards"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    """List cards with pagination and optional filters."""
    query = db.query(Axis1CardModel)
    query, params = _apply_card_filters(
        query,
        q=None,
        colors=colors,
        color_identity=color_identity,
        types=types,
        supertypes=supertypes,
        subtypes=subtypes,
        keywords=keywords,
        rarity=rarity,
        set_code=set_code,
        layout=layout,
        produced_mana=produced_mana,
        lang=lang,
        cmc_min=cmc_min,
        cmc_max=cmc_max,
        power_min=power_min,
        power_max=power_max,
        toughness_min=toughness_min,
        toughness_max=toughness_max,
        loyalty_min=loyalty_min,
        loyalty_max=loyalty_max,
        is_legendary=is_legendary,
    )
    if params:
        query = query.params(**params)
    
    # Get total count (before pagination)
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    cards = query.offset(offset).limit(page_size).all()
    
    # Convert to response models
    card_responses = [card_model_to_response(card) for card in cards]
    
    return SearchResponse(
        cards=card_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(cards)) < total
    )

