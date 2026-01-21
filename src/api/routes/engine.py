from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
import time
import os

from api.routes.auth import get_current_user
from api.schemas.engine_schemas import (
    EngineActionRequest,
    EngineActionResponse,
    GameStateSnapshot,
    CreateGameSessionRequest,
    GameSessionResponse,
)
from db.models import User
from db.models import GameSession
from db.connection import SessionLocal
from engine import (
    AbilityGraphRuntimeAdapter,
    AbilityRegistry,
    CombatState,
    GameObject,
    GameState,
    PlayerState,
    ResolveContext,
    StackItem,
    TurnManager,
    TurnState,
)
from engine.continuous import apply_continuous_effects
from engine.sba import apply_state_based_actions
from engine.rules import (
    assign_combat_damage,
    cast_spell,
    declare_attackers,
    declare_blockers,
    activate_mana_ability,
    activate_ability,
    play_land,
    prepare_cast,
)
from engine.turn import Phase, Step
from engine.zones import ZONE_BATTLEFIELD, ZONE_COMMAND, ZONE_HAND


router = APIRouter(prefix="/api/engine", tags=["engine"])

_GAME_SESSION_CACHE: dict[str, GameState] = {}
_GAME_SESSION_META: dict[str, dict] = {}
_SNAPSHOT_EVERY_ACTIONS = int(os.getenv("SNAPSHOT_EVERY_ACTIONS", "5"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_cached_session(game_id: str) -> GameState | None:
    return _GAME_SESSION_CACHE.get(game_id)


def _cache_session(game_id: str, game_state: GameState, version: int, user_id: int | None = None) -> None:
    _GAME_SESSION_CACHE[game_id] = game_state
    meta = _GAME_SESSION_META.setdefault(game_id, {"version": version, "action_count": 0, "last_snapshot_version": version})
    if user_id is not None:
        meta["user_id"] = user_id


def _hydrate_session_from_db(db: Session, game_id: str, user_id: int) -> tuple[GameState, int]:
    session = db.query(GameSession).filter_by(game_id=game_id, user_id=user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found.")
    snapshot = GameStateSnapshot(**session.snapshot_json)
    game_state = _build_game_state(snapshot)
    _cache_session(game_id, game_state, session.version, user_id=user_id)
    return game_state, session.version


def _persist_snapshot(db: Session, game_id: str, snapshot: GameStateSnapshot, user_id: int) -> int:
    session = db.query(GameSession).filter_by(game_id=game_id, user_id=user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found.")
    session.snapshot_json = snapshot.model_dump()
    session.version = int(session.version or 0) + 1
    db.add(session)
    db.commit()
    db.refresh(session)
    return session.version


def _should_snapshot(meta: dict) -> bool:
    meta["action_count"] = meta.get("action_count", 0) + 1
    return meta["action_count"] >= _SNAPSHOT_EVERY_ACTIONS


def _maybe_snapshot(
    db: Session,
    game_id: str,
    pre_turn_number: int,
    pre_step,
    pre_stack_len: int,
    game_state: GameState,
    session_version: int,
    user_id: int,
) -> None:
    meta = _GAME_SESSION_META.setdefault(game_id, {
        "version": session_version or 1,
        "action_count": 0,
        "last_snapshot_version": session_version or 1,
    })
    snapshot_needed = (
        game_state.turn.turn_number != pre_turn_number
        or game_state.turn.step != pre_step
        or len(game_state.stack.items) < pre_stack_len
        or _should_snapshot(meta)
    )
    if not snapshot_needed:
        return
    snapshot = _serialize_game_state(game_state)
    new_version = _persist_snapshot(db, game_id, snapshot, user_id=user_id)
    meta["version"] = new_version
    meta["last_snapshot_version"] = new_version
    meta["action_count"] = 0


def _build_game_state(snapshot: GameStateSnapshot) -> GameState:
    players = []
    for player in snapshot.players:
        players.append(PlayerState(
            id=player.id,
            life=player.life,
            max_hand_size=getattr(player, "max_hand_size", 7),
            has_lost=getattr(player, "has_lost", False),
            removed_from_game=getattr(player, "removed_from_game", False),
            poison_counters=getattr(player, "poison_counters", 0),
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
            mana_cost=obj.mana_cost,
            base_name=getattr(obj, "base_name", None),
            base_mana_cost=getattr(obj, "base_mana_cost", None),
            base_mana_value=getattr(obj, "base_mana_value", None),
            base_types=list(obj.base_types) if hasattr(obj, "base_types") else list(obj.types),
            colors=list(obj.colors),
            base_colors=list(obj.base_colors) if hasattr(obj, "base_colors") else list(obj.colors),
            type_line=obj.type_line,
            base_type_line=getattr(obj, "base_type_line", None),
            oracle_text=obj.oracle_text,
            base_oracle_text=getattr(obj, "base_oracle_text", None),
            mana_value=obj.mana_value,
            power=obj.power,
            toughness=obj.toughness,
            base_power=obj.base_power,
            base_toughness=obj.base_toughness,
            cda_power=getattr(obj, "cda_power", None),
            cda_toughness=getattr(obj, "cda_toughness", None),
            entered_turn=obj.entered_turn,
            tapped=obj.tapped,
            damage=obj.damage,
            counters=dict(obj.counters),
            keywords=set(obj.keywords),
            base_keywords=set(obj.base_keywords),
            protections=set(obj.protections),
            attached_to=obj.attached_to,
            is_token=obj.is_token,
            was_cast=obj.was_cast,
            is_attacking=obj.is_attacking,
            is_blocking=obj.is_blocking,
            phased_out=obj.phased_out,
            transformed=obj.transformed,
            regenerate_shield=obj.regenerate_shield,
            ability_graphs=list(obj.ability_graphs),
            base_ability_graphs=list(getattr(obj, "base_ability_graphs", [])),
            temporary_effects=list(getattr(obj, "temporary_effects", [])),
            activation_limits=dict(getattr(obj, "activation_limits", {})),
            etb_choices=dict(getattr(obj, "etb_choices", {})),
            base_etb_choices=dict(getattr(obj, "etb_choices", {})),
        )

    # Filter zone lists to only include valid object IDs
    valid_ids = set(game_state.objects.keys())
    for player in game_state.players:
        player.library = [obj_id for obj_id in player.library if obj_id in valid_ids]
        player.hand = [obj_id for obj_id in player.hand if obj_id in valid_ids]
        player.graveyard = [obj_id for obj_id in player.graveyard if obj_id in valid_ids]
        player.exile = [obj_id for obj_id in player.exile if obj_id in valid_ids]
        player.command = [obj_id for obj_id in player.command if obj_id in valid_ids]
        player.battlefield = [obj_id for obj_id in player.battlefield if obj_id in valid_ids]

    game_state.stack.items = [
        StackItem(kind=item.kind, payload=item.payload, controller_id=item.controller_id)
        for item in snapshot.stack
    ]

    combat_state = None
    if snapshot.turn.combat_state:
        combat_state = CombatState(
            attacking_player_id=snapshot.turn.combat_state.attacking_player_id,
            defending_player_id=snapshot.turn.combat_state.defending_player_id,
            defending_object_id=getattr(snapshot.turn.combat_state, "defending_object_id", None),
            attackers=list(snapshot.turn.combat_state.attackers),
            blockers=dict(snapshot.turn.combat_state.blockers),
            attackers_declared=getattr(snapshot.turn.combat_state, "attackers_declared", False),
            blockers_declared=getattr(snapshot.turn.combat_state, "blockers_declared", False),
            first_strike_resolved=getattr(snapshot.turn.combat_state, "first_strike_resolved", False),
            combat_damage_resolved=getattr(snapshot.turn.combat_state, "combat_damage_resolved", False),
        )

    try:
        game_state.turn = TurnState(
            turn_number=snapshot.turn.turn_number,
            active_player_index=snapshot.turn.active_player_index,
            phase=Phase(snapshot.turn.phase),
            step=Step(snapshot.turn.step),
            land_plays_this_turn=getattr(snapshot.turn, "land_plays_this_turn", 0),
            combat_state=combat_state,
            priority_current_index=getattr(snapshot.turn, "priority_current_index", 0),
            priority_pass_count=getattr(snapshot.turn, "priority_pass_count", 0),
            priority_last_passed_player_id=getattr(snapshot.turn, "priority_last_passed_player_id", None),
        )
    except ValueError:
        game_state.turn = TurnState()

    game_state.debug_log = list(snapshot.debug_log)
    game_state.replacement_effects = list(snapshot.replacement_effects)
    game_state.replacement_choices = dict(snapshot.replacement_choices or {})
    game_state.choices = dict(snapshot.choices or {})
    game_state.pending_triggers = list(snapshot.pending_triggers or [])
    game_state.prepared_casts = dict(snapshot.prepared_casts or {})
    game_state.pending_search_selections = dict(snapshot.pending_search_selections or {})
    return game_state


def _serialize_game_state(game_state: GameState) -> GameStateSnapshot:
    combat_state = None
    if game_state.turn.combat_state:
        combat_state = {
            "attacking_player_id": game_state.turn.combat_state.attacking_player_id,
            "defending_player_id": game_state.turn.combat_state.defending_player_id,
            "defending_object_id": game_state.turn.combat_state.defending_object_id,
            "attackers": list(game_state.turn.combat_state.attackers),
            "blockers": dict(game_state.turn.combat_state.blockers),
            "attackers_declared": game_state.turn.combat_state.attackers_declared,
            "blockers_declared": game_state.turn.combat_state.blockers_declared,
            "first_strike_resolved": game_state.turn.combat_state.first_strike_resolved,
            "combat_damage_resolved": game_state.turn.combat_state.combat_damage_resolved,
        }

    return GameStateSnapshot(
        players=[
            {
                "id": player.id,
                "life": player.life,
                "max_hand_size": getattr(player, "max_hand_size", 7),
                "has_lost": getattr(player, "has_lost", False),
                "removed_from_game": getattr(player, "removed_from_game", False),
                "poison_counters": getattr(player, "poison_counters", 0),
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
                "mana_cost": obj.mana_cost,
                "base_name": getattr(obj, "base_name", None),
                "base_mana_cost": getattr(obj, "base_mana_cost", None),
                "base_mana_value": getattr(obj, "base_mana_value", None),
                "base_types": list(obj.base_types) if hasattr(obj, "base_types") else list(obj.types),
                "colors": list(obj.colors),
                "base_colors": list(obj.base_colors) if hasattr(obj, "base_colors") else list(obj.colors),
                "type_line": obj.type_line,
                "base_type_line": getattr(obj, "base_type_line", None),
                "oracle_text": obj.oracle_text,
                "base_oracle_text": getattr(obj, "base_oracle_text", None),
                "mana_value": obj.mana_value,
                "power": obj.power,
                "toughness": obj.toughness,
                "base_power": obj.base_power,
                "base_toughness": obj.base_toughness,
                "cda_power": getattr(obj, "cda_power", None),
                "cda_toughness": getattr(obj, "cda_toughness", None),
                "entered_turn": obj.entered_turn,
                "tapped": obj.tapped,
                "damage": obj.damage,
                "counters": obj.counters,
                "keywords": list(obj.keywords),
                "base_keywords": list(obj.base_keywords),
                "protections": list(obj.protections),
                "attached_to": obj.attached_to,
                "is_token": obj.is_token,
                "was_cast": obj.was_cast,
                "is_attacking": obj.is_attacking,
                "is_blocking": obj.is_blocking,
                "phased_out": obj.phased_out,
                "transformed": obj.transformed,
                "regenerate_shield": obj.regenerate_shield,
                "ability_graphs": list(obj.ability_graphs),
                "base_ability_graphs": list(getattr(obj, "base_ability_graphs", [])),
                "temporary_effects": list(getattr(obj, "temporary_effects", [])),
                "activation_limits": dict(getattr(obj, "activation_limits", {})),
                "etb_choices": dict(getattr(obj, "etb_choices", {})),
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
            "land_plays_this_turn": game_state.turn.land_plays_this_turn,
            "combat_state": combat_state,
            "priority_current_index": game_state.turn.priority_current_index,
            "priority_pass_count": game_state.turn.priority_pass_count,
            "priority_last_passed_player_id": game_state.turn.priority_last_passed_player_id,
        },
        debug_log=game_state.debug_log,
        replacement_effects=list(game_state.replacement_effects),
        replacement_choices=dict(game_state.replacement_choices),
        choices=dict(game_state.choices),
        pending_triggers=list(game_state.pending_triggers),
        prepared_casts=dict(game_state.prepared_casts),
        pending_search_selections=dict(game_state.pending_search_selections),
    )


@router.post("/sessions", response_model=GameSessionResponse)
def create_game_session(
    payload: CreateGameSessionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game_id = str(uuid4())
    snapshot = payload.game_state
    session = GameSession(
        game_id=game_id,
        user_id=user.id,
        snapshot_json=snapshot.model_dump(),
        version=1,
    )
    db.add(session)
    db.commit()
    _cache_session(game_id, _build_game_state(snapshot), session.version, user_id=user.id)
    return GameSessionResponse(game_id=game_id, game_state=snapshot, version=session.version)


@router.get("/sessions/{game_id}", response_model=GameSessionResponse)
def get_game_session(
    game_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cached = _get_cached_session(game_id)
    meta = _GAME_SESSION_META.get(game_id, {})
    if cached and meta.get("user_id") == user.id:
        snapshot = _serialize_game_state(cached)
        return GameSessionResponse(game_id=game_id, game_state=snapshot, version=int(meta.get("version", 1)))
    session = db.query(GameSession).filter_by(game_id=game_id, user_id=user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found.")
    snapshot = GameStateSnapshot(**session.snapshot_json)
    _cache_session(game_id, _build_game_state(snapshot), session.version, user_id=user.id)
    return GameSessionResponse(game_id=game_id, game_state=snapshot, version=session.version)


@router.post("/execute", response_model=EngineActionResponse)
def execute_engine_action(
    payload: EngineActionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print(f"[engine] execute action={payload.action} game_id={payload.game_id}", flush=True)
    action = payload.action
    game_state: GameState | None = None
    session_version = 0

    if action in ("resolve_graph", "check_targets"):
        if not payload.game_state:
            raise HTTPException(status_code=400, detail="game_state is required for this action")
        game_state = _build_game_state(payload.game_state)
    else:
        if not payload.game_id:
            raise HTTPException(status_code=400, detail="game_id is required for this action")
        cached = _get_cached_session(payload.game_id)
        meta = _GAME_SESSION_META.get(payload.game_id, {})
        if cached and meta.get("user_id") == user.id:
            game_state = cached
            session_version = int(meta.get("version", 1))
        else:
            game_state, session_version = _hydrate_session_from_db(db, payload.game_id, user.id)

    if action in ("resolve_graph", "check_targets"):
        AbilityRegistry(game_state)
    else:
        if not getattr(game_state, "_ability_registry", None):
            game_state._ability_registry = AbilityRegistry(game_state)
    if payload.replacement_choices:
        game_state.replacement_choices = dict(payload.replacement_choices)

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
        from engine.targets import normalize_targets, validate_targets
        from engine.choices import validate_enter_choices, validate_modal_choices
        try:
            normalize_targets(game_state, context)
            validate_targets(game_state, context)
            validate_enter_choices(payload.ability_graph.model_dump() if payload.ability_graph else None, context.__dict__)
            validate_modal_choices(payload.ability_graph.model_dump() if payload.ability_graph else None, context.__dict__)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        adapter = AbilityGraphRuntimeAdapter(game_state)
        result = adapter.resolve(payload.ability_graph.model_dump(), context)
        if context.source_id:
            game_state.event_bus.publish(Event(
                type="ability_resolved",
                payload={"source_id": context.source_id, "controller_id": context.controller_id},
            ))
        apply_continuous_effects(game_state)
        apply_state_based_actions(game_state)
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result=result,
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "check_targets":
        contexts = payload.contexts or []
        if payload.context:
            contexts = contexts + [payload.context]
        if not contexts:
            raise HTTPException(status_code=400, detail="context or contexts are required for check_targets")
        from engine.targets import get_target_issues, has_legal_targets, normalize_targets
        checks = []
        for ctx in contexts:
            context = ResolveContext(
                source_id=ctx.source_id,
                controller_id=ctx.controller_id,
                triggering_source_id=ctx.triggering_source_id,
                triggering_aura_id=ctx.triggering_aura_id,
                triggering_spell_id=ctx.triggering_spell_id,
                targets=ctx.targets,
                targets_by_effect=ctx.targets_by_effect,
                required_targets_by_effect=ctx.required_targets_by_effect,
                distinct_targets_by_effect=ctx.distinct_targets_by_effect,
                min_targets_by_effect=ctx.min_targets_by_effect,
                choices=ctx.choices,
                previous_results=ctx.previous_results,
            )
            normalize_targets(game_state, context)
            issues = get_target_issues(game_state, context)
            checks.append({
                "legal": has_legal_targets(game_state, context),
                "targets": context.targets,
                "issues": issues,
            })
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"checks": checks},
            debug_log=game_state.debug_log,
        )

    pre_turn_number = game_state.turn.turn_number
    pre_step = game_state.turn.step
    pre_stack_len = len(game_state.stack.items)

    if action == "advance_turn":
        print(
            f"[engine] advance_turn start game_id={payload.game_id} "
            f"turn={game_state.turn.turn_number} {game_state.turn.phase.value}:{game_state.turn.step.value}",
            flush=True,
        )
        turn_manager = TurnManager(game_state)
        turn_manager._advance_phase_step()
        print(
            f"[engine] advance_turn end game_id={payload.game_id} "
            f"turn={game_state.turn.turn_number} {game_state.turn.phase.value}:{game_state.turn.step.value}",
            flush=True,
        )
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={
                "status": "advanced",
                "phase": game_state.turn.phase.value,
                "step": game_state.turn.step.value,
                "current_priority": turn_manager.priority.current,
            },
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "pass_priority":
        player_id = payload.player_id
        if player_id is None:
            raise HTTPException(status_code=400, detail="player_id is required for pass_priority")
        
        # Debug: Check pending_search_selections before handling pass
        print(f"[engine] pass_priority player={player_id} pending_search_selections_before={game_state.pending_search_selections}", flush=True)
        
        turn_manager = TurnManager(game_state)
        
        # Build provided context from payload
        provided_context = None
        if payload.targets_by_effect:
            provided_context = {"targets_by_effect": payload.targets_by_effect}
        
        print(f"[engine] pass_priority player={player_id} targets_by_effect={payload.targets_by_effect}", flush=True)
        
        pass_result = turn_manager.handle_player_pass(player_id, provided_context)
        
        # Debug: Check pending_search_selections after handling pass
        print(f"[engine] pass_priority pending_search_selections_after={game_state.pending_search_selections}", flush=True)
        print(f"[engine] pass_priority result={pass_result}", flush=True)
        
        # Check if input is needed
        if pass_result.get("status") == "needs_input":
            response = EngineActionResponse(
                game_state=_serialize_game_state(game_state),
                result={
                    "status": "needs_input",
                    "current_priority": turn_manager.priority.current,
                    "pending_search_choices": pass_result.get("pending_search_choices", []),
                },
                debug_log=game_state.debug_log,
            )
            # Don't snapshot - we're waiting for input
            return response
        
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "passed", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "play_land":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for play_land")
        turn_manager = TurnManager(game_state)
        try:
            play_land(game_state, turn_manager, payload.player_id, payload.object_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "land_played", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "prepare_cast":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for prepare_cast")
        turn_manager = TurnManager(game_state)
        try:
            context = payload.context.model_dump() if payload.context else None
            result = prepare_cast(
                game_state,
                turn_manager,
                payload.player_id,
                payload.object_id,
                payload.x_value or 0,
                ability_graph=payload.ability_graph.model_dump() if payload.ability_graph else None,
                context=context,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result=result,
            debug_log=game_state.debug_log,
        )

    if action == "finalize_cast":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for finalize_cast")
        turn_manager = TurnManager(game_state)
        try:
            ability_graph = payload.ability_graph.model_dump() if payload.ability_graph else None
            prepared_cast = game_state.prepared_casts.get(payload.player_id)
            if not prepared_cast:
                raise ValueError("No prepared cast found for player.")
            if prepared_cast.get("object_id") != payload.object_id:
                raise ValueError("Prepared cast does not match selected card.")
            prepared_context = prepared_cast.get("context") or {}
            payload_context = payload.context.model_dump() if payload.context else {}
            merged_context = {
                **prepared_context,
                **payload_context,
                "targets": {
                    **(prepared_context.get("targets") or {}),
                    **(payload_context.get("targets") or {}),
                },
                "choices": {
                    **(prepared_context.get("choices") or {}),
                    **(payload_context.get("choices") or {}),
                },
            }
            context = merged_context if merged_context else None
            x_value = prepared_cast.get("x_value") or 0
            cast_spell(
                game_state,
                turn_manager,
                payload.player_id,
                payload.object_id,
                x_value,
                ability_graph=ability_graph,
                context=context,
                mana_payment=payload.mana_payment or None,
                mana_payment_detail=payload.mana_payment_detail.model_dump() if payload.mana_payment_detail else None,
            )
            game_state.prepared_casts.pop(payload.player_id, None)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "spell_cast", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "cast_spell":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for cast_spell")
        turn_manager = TurnManager(game_state)
        try:
            ability_graph = payload.ability_graph.model_dump() if payload.ability_graph else None
            context = payload.context.model_dump() if payload.context else None
            cast_spell(
                game_state,
                turn_manager,
                payload.player_id,
                payload.object_id,
                payload.x_value or 0,
                ability_graph=ability_graph,
                context=context,
                mana_payment=payload.mana_payment or None,
                mana_payment_detail=payload.mana_payment_detail.model_dump() if payload.mana_payment_detail else None,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "spell_cast", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "activate_mana_ability":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for activate_mana_ability")
        turn_manager = TurnManager(game_state)
        try:
            activate_mana_ability(game_state, turn_manager, payload.player_id, payload.object_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "mana_added", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "activate_ability":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for activate_ability")
        turn_manager = TurnManager(game_state)
        try:
            activate_ability(
                game_state,
                turn_manager,
                payload.player_id,
                payload.object_id,
                payload.ability_index or 0,
                payload.context.model_dump() if payload.context else None,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "ability_activated", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "declare_attackers":
        if payload.player_id is None:
            raise HTTPException(status_code=400, detail="player_id is required for declare_attackers")
        turn_manager = TurnManager(game_state)
        try:
            declare_attackers(
                game_state,
                turn_manager,
                payload.player_id,
                payload.attackers,
                payload.defending_player_id,
                payload.defending_object_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "attackers_declared", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "declare_blockers":
        if payload.player_id is None:
            raise HTTPException(status_code=400, detail="player_id is required for declare_blockers")
        turn_manager = TurnManager(game_state)
        try:
            declare_blockers(game_state, turn_manager, payload.player_id, payload.blockers)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "blockers_declared", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    if action == "assign_combat_damage":
        if payload.player_id is None:
            raise HTTPException(status_code=400, detail="player_id is required for assign_combat_damage")
        turn_manager = TurnManager(game_state)
        try:
            assign_combat_damage(
                game_state,
                turn_manager,
                payload.player_id,
                payload.damage_assignments or None,
                payload.combat_damage_pass,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        response = EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "combat_damage_assigned", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )
        _maybe_snapshot(db, payload.game_id, pre_turn_number, pre_step, pre_stack_len, game_state, session_version, user.id)
        return response

    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
