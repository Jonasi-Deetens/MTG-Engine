from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.routes.auth import get_current_user
from api.schemas.unified_effect_schemas import (
    CardEffectGraphResponse,
    EffectGraph,
    EffectValidationResponse,
)
from db.connection import SessionLocal
from db.models import Axis1CardModel, CardEffectGraph, User

router = APIRouter(prefix="/api/effects", tags=["effects"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/validate", response_model=EffectValidationResponse)
def validate_effect_graph(
    graph: EffectGraph,
    user: User = Depends(get_current_user),
):
    """Validate unified effect graph (same rules as frontend zod schema)."""
    try:
        EffectGraph.model_validate(graph.model_dump(by_alias=True))
        return EffectValidationResponse(valid=True, errors=[])
    except ValidationError as exc:
        errors = [err["msg"] for err in exc.errors()]
        return EffectValidationResponse(valid=False, errors=errors)


@router.post("/cards/{card_id}/effects", response_model=CardEffectGraphResponse)
def save_card_effect_graph(
    card_id: str,
    effect_graph: EffectGraph,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    card_id_str = str(card_id).strip()
    if card_id_str == "":
        raise HTTPException(status_code=400, detail="Invalid card_id provided: card_id is empty")
    if card_id_str.lower() in ("undefined", "null"):
        raise HTTPException(status_code=400, detail=f"Invalid card_id provided: '{card_id_str}'")
    card_id = card_id_str

    card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    if not card.name:
        raise HTTPException(status_code=404, detail="Card name not found")

    all_versions = db.query(Axis1CardModel).filter(Axis1CardModel.name == card.name).all()
    if not all_versions:
        raise HTTPException(status_code=404, detail="No card versions found")

    saved_graphs = []
    for version in all_versions:
        existing = db.query(CardEffectGraph).filter(
            CardEffectGraph.card_id == version.card_id,
            CardEffectGraph.user_id == user.id,
        ).first()

        if existing:
            existing.effect_graph_json = effect_graph.model_dump(by_alias=True)
            existing.updated_at = datetime.utcnow()
            saved_graphs.append(existing)
        else:
            new_graph = CardEffectGraph(
                card_id=version.card_id,
                user_id=user.id,
                effect_graph_json=effect_graph.model_dump(by_alias=True),
            )
            db.add(new_graph)
            saved_graphs.append(new_graph)

    db.commit()

    for graph in saved_graphs:
        db.refresh(graph)

    result = next((g for g in saved_graphs if g.card_id == card_id), saved_graphs[0])

    return CardEffectGraphResponse(
        id=result.id,
        card_id=result.card_id,
        effect_graph=EffectGraph(**result.effect_graph_json),
        created_at=result.created_at.isoformat(),
        updated_at=result.updated_at.isoformat(),
    )


def _find_card_effect_graph(
    db: Session,
    user: User,
    card_id: str,
) -> Optional[CardEffectGraphResponse]:
    graph = db.query(CardEffectGraph).filter(
        CardEffectGraph.card_id == card_id,
        CardEffectGraph.user_id == user.id,
    ).first()

    if graph:
        return CardEffectGraphResponse(
            id=graph.id,
            card_id=graph.card_id,
            effect_graph=EffectGraph(**graph.effect_graph_json),
            created_at=graph.created_at.isoformat(),
            updated_at=graph.updated_at.isoformat(),
        )

    card = db.query(Axis1CardModel).filter(Axis1CardModel.card_id == card_id).first()
    if not card or not card.name:
        return None

    all_versions = db.query(Axis1CardModel).filter(Axis1CardModel.name == card.name).all()
    for version in all_versions:
        graph = db.query(CardEffectGraph).filter(
            CardEffectGraph.card_id == version.card_id,
            CardEffectGraph.user_id == user.id,
        ).first()
        if graph:
            return CardEffectGraphResponse(
                id=graph.id,
                card_id=card_id,
                effect_graph=EffectGraph(**graph.effect_graph_json),
                created_at=graph.created_at.isoformat(),
                updated_at=graph.updated_at.isoformat(),
            )

    return None


@router.get("/cards/{card_id}/effects", response_model=CardEffectGraphResponse)
def get_card_effect_graph(
    card_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    response = _find_card_effect_graph(db, user, card_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Effect graph not found for this card or its versions")
    return response
