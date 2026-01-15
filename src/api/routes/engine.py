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
            mana_cost=obj.mana_cost,
            base_types=list(obj.base_types) if hasattr(obj, "base_types") else list(obj.types),
            colors=list(obj.colors),
            base_colors=list(obj.base_colors) if hasattr(obj, "base_colors") else list(obj.colors),
            type_line=obj.type_line,
            oracle_text=obj.oracle_text,
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
            temporary_effects=list(getattr(obj, "temporary_effects", [])),
        )

    game_state.stack.items = [
        StackItem(kind=item.kind, payload=item.payload, controller_id=item.controller_id)
        for item in snapshot.stack
    ]

    combat_state = None
    if snapshot.turn.combat_state:
        combat_state = CombatState(
            attacking_player_id=snapshot.turn.combat_state.attacking_player_id,
            defending_player_id=snapshot.turn.combat_state.defending_player_id,
            attackers=list(snapshot.turn.combat_state.attackers),
            blockers=dict(snapshot.turn.combat_state.blockers),
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
    game_state.prepared_casts = dict(snapshot.prepared_casts or {})
    return game_state


def _serialize_game_state(game_state: GameState) -> GameStateSnapshot:
    combat_state = None
    if game_state.turn.combat_state:
        combat_state = {
            "attacking_player_id": game_state.turn.combat_state.attacking_player_id,
            "defending_player_id": game_state.turn.combat_state.defending_player_id,
            "attackers": list(game_state.turn.combat_state.attackers),
            "blockers": dict(game_state.turn.combat_state.blockers),
        }

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
                "mana_cost": obj.mana_cost,
                "base_types": list(obj.base_types) if hasattr(obj, "base_types") else list(obj.types),
                "colors": list(obj.colors),
                "base_colors": list(obj.base_colors) if hasattr(obj, "base_colors") else list(obj.colors),
                "type_line": obj.type_line,
                "oracle_text": obj.oracle_text,
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
                "temporary_effects": list(getattr(obj, "temporary_effects", [])),
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
        prepared_casts=dict(game_state.prepared_casts),
    )


@router.post("/execute", response_model=EngineActionResponse)
def execute_engine_action(
    payload: EngineActionRequest,
    user: User = Depends(get_current_user),
):
    game_state = _build_game_state(payload.game_state)
    AbilityRegistry(game_state)
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
        from engine.targets import normalize_targets, validate_targets
        try:
            normalize_targets(game_state, context)
            validate_targets(game_state, context)
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
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result=result,
            debug_log=game_state.debug_log,
        )

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

    if action == "advance_turn":
        turn_manager = TurnManager(game_state)
        turn_manager._advance_phase_step()
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={
                "status": "advanced",
                "phase": game_state.turn.phase.value,
                "step": game_state.turn.step.value,
                "current_priority": turn_manager.priority.current,
            },
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

    if action == "play_land":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for play_land")
        turn_manager = TurnManager(game_state)
        try:
            play_land(game_state, turn_manager, payload.player_id, payload.object_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "land_played", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

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
            context = prepared_cast.get("context") or (payload.context.model_dump() if payload.context else None)
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
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "spell_cast", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

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
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "spell_cast", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

    if action == "activate_mana_ability":
        if payload.player_id is None or payload.object_id is None:
            raise HTTPException(status_code=400, detail="player_id and object_id are required for activate_mana_ability")
        turn_manager = TurnManager(game_state)
        try:
            activate_mana_ability(game_state, turn_manager, payload.player_id, payload.object_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "mana_added", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

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
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "ability_activated", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

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
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "attackers_declared", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

    if action == "declare_blockers":
        if payload.player_id is None:
            raise HTTPException(status_code=400, detail="player_id is required for declare_blockers")
        turn_manager = TurnManager(game_state)
        try:
            declare_blockers(game_state, turn_manager, payload.player_id, payload.blockers)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "blockers_declared", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

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
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return EngineActionResponse(
            game_state=_serialize_game_state(game_state),
            result={"status": "combat_damage_assigned", "current_priority": turn_manager.priority.current},
            debug_log=game_state.debug_log,
        )

    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
