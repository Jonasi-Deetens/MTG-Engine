from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.routes.auth import get_current_user
from api.schemas.engine_schemas import (
    EngineActionRequest,
    EngineActionResponse,
    GameStateSnapshot,
)
from db.models import User
from engine import (
    AbilityGraphRuntimeAdapter,
    GameObject,
    GameState,
    PlayerState,
    ResolveContext,
    StackItem,
    TurnManager,
    TurnState,
)
from engine.turn import Phase, Step


router = APIRouter(prefix="/api/engine", tags=["engine"])


def _build_game_state(snapshot: GameStateSnapshot) -> GameState:
    players = []
    for player in snapshot.players:
        players.append(PlayerState(
            id=player.id,
            life=player.life,
            mana_pool=player.mana_pool,
            library=list(player.library),
            hand=list(player.hand),
            graveyard=list(player.graveyard),
            exile=list(player.exile),
            command=list(player.command),
            battlefield=list(player.battlefield),
            commander_id=player.commander_id,
            commander_tax=player.commander_tax,
            commander_damage_taken=player.commander_damage_taken,
        ))

    game_state = GameState(players=players)

    for obj in snapshot.objects:
        game_state.objects[obj.id] = GameObject(
            id=obj.id,
            name=obj.name,
            owner_id=obj.owner_id,
            controller_id=obj.controller_id,
            types=list(obj.types),
            zone=obj.zone,
            mana_value=obj.mana_value,
            power=obj.power,
            toughness=obj.toughness,
            tapped=obj.tapped,
            damage=obj.damage,
            counters=dict(obj.counters),
            keywords=set(obj.keywords),
            protections=set(obj.protections),
            attached_to=obj.attached_to,
            is_token=obj.is_token,
            was_cast=obj.was_cast,
            is_attacking=obj.is_attacking,
            is_blocking=obj.is_blocking,
            phased_out=obj.phased_out,
            transformed=obj.transformed,
            regenerate_shield=obj.regenerate_shield,
        )

    game_state.stack.items = [
        StackItem(kind=item.kind, payload=item.payload, controller_id=item.controller_id)
        for item in snapshot.stack
    ]

    try:
        game_state.turn = TurnState(
            turn_number=snapshot.turn.turn_number,
            active_player_index=snapshot.turn.active_player_index,
            phase=Phase(snapshot.turn.phase),
            step=Step(snapshot.turn.step),
        )
    except ValueError:
        game_state.turn = TurnState()

    game_state.debug_log = list(snapshot.debug_log)
    return game_state


def _serialize_game_state(game_state: GameState) -> GameStateSnapshot:
    return GameStateSnapshot(
        players=[
            {
                "id": player.id,
                "life": player.life,
                "mana_pool": player.mana_pool,
                "library": player.library,
                "hand": player.hand,
                "graveyard": player.graveyard,
                "exile": player.exile,
                "command": player.command,
                "battlefield": player.battlefield,
                "commander_id": player.commander_id,
                "commander_tax": player.commander_tax,
                "commander_damage_taken": player.commander_damage_taken,
            }
            for player in game_state.players
        ],
        objects=[
            {
                "id": obj.id,
                "name": obj.name,
                "owner_id": obj.owner_id,
                "controller_id": obj.controller_id,
                "types": obj.types,
                "zone": obj.zone,
                "mana_value": obj.mana_value,
                "power": obj.power,
                "toughness": obj.toughness,
                "tapped": obj.tapped,
                "damage": obj.damage,
                "counters": obj.counters,
                "keywords": list(obj.keywords),
                "protections": list(obj.protections),
                "attached_to": obj.attached_to,
                "is_token": obj.is_token,
                "was_cast": obj.was_cast,
                "is_attacking": obj.is_attacking,
                "is_blocking": obj.is_blocking,
                "phased_out": obj.phased_out,
                "transformed": obj.transformed,
                "regenerate_shield": obj.regenerate_shield,
            }
            for obj in game_state.objects.values()
        ],
        stack=[
            {
                "kind": item.kind,
                "payload": item.payload,
                "controller_id": item.controller_id,
            }
            for item in game_state.stack.items
        ],
        turn={
            "turn_number": game_state.turn.turn_number,
            "active_player_index": game_state.turn.active_player_index,
            "phase": game_state.turn.phase.value,
            "step": game_state.turn.step.value,
        },
        debug_log=game_state.debug_log,
    )


@router.post("/execute", response_model=EngineActionResponse)
def execute_engine_action(
    payload: EngineActionRequest,
    user: User = Depends(get_current_user),
):
    game_state = _build_game_state(payload.game_state)
    action = payload.action

    if action == "resolve_graph":
        if not payload.ability_graph:
            raise HTTPException(status_code=400, detail="ability_graph is required for resolve_graph")
        context = ResolveContext()
        if payload.context:
            context = ResolveContext(
                source_id=payload.context.source_id,
                controller_id=payload.context.controller_id,
                triggering_source_id=payload.context.triggering_source_id,
                triggering_aura_id=payload.context.triggering_aura_id,
                triggering_spell_id=payload.context.triggering_spell_id,
                targets=payload.context.targets,
                choices=payload.context.choices,
                previous_results=payload.context.previous_results,
            )
        adapter = AbilityGraphRuntimeAdapter(game_state)
        result = adapter.resolve(payload.ability_graph.model_dump(), context)
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result=result,
            debug_log=game_state.debug_log,
        )

    if action == "advance_turn":
        turn_manager = TurnManager(game_state)
        turn_manager._advance_phase_step()
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "advanced", "phase": game_state.turn.phase.value, "step": game_state.turn.step.value},
            debug_log=game_state.debug_log,
        )

    if action == "pass_priority":
        player_id = payload.player_id
        if player_id is None:
            raise HTTPException(status_code=400, detail="player_id is required for pass_priority")
        turn_manager = TurnManager(game_state)
        turn_manager.handle_player_pass(player_id)
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "passed", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
