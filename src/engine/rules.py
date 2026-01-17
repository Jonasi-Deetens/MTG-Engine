from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ability_graph import AbilityGraphRuntimeAdapter
from .combat import CombatState
from .combat_damage import resolve_combat_damage
from .commander import apply_commander_tax
from .mana import (
    can_pay_cost,
    mana_cost_snapshot,
    parse_mana_cost,
    pay_cost,
    pay_cost_with_payment,
    produce_mana_for_object,
)
from .stack import StackItem
from .targets import normalize_targets, validate_targets
from .turn import Phase, Step
from .zones import ZONE_BATTLEFIELD, ZONE_COMMAND, ZONE_GRAVEYARD, ZONE_HAND
from .events import Event
from .state import ResolveContext
from .choices import validate_enter_choices


def require_priority(turn_manager, player_id: int) -> None:
    if player_id != turn_manager.priority.current:
        raise ValueError("Player does not have priority.")


def require_active_player(turn_manager, player_id: int) -> None:
    if player_id != turn_manager.current_active_player_id():
        raise ValueError("Only the active player can perform this action.")


def require_main_phase(game_state) -> None:
    if game_state.turn.step not in (Step.PRECOMBAT_MAIN, Step.POSTCOMBAT_MAIN):
        raise ValueError("Action only allowed during a main phase.")


def require_empty_stack(game_state) -> None:
    if not game_state.stack.is_empty():
        raise ValueError("Action not allowed while the stack is not empty.")


def play_land(game_state, turn_manager, player_id: int, object_id: str) -> None:
    require_priority(turn_manager, player_id)
    require_active_player(turn_manager, player_id)
    require_main_phase(game_state)
    require_empty_stack(game_state)

    if game_state.turn.land_plays_this_turn >= 1:
        raise ValueError("Land already played this turn.")

    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Card not found.")
    if obj.zone != ZONE_HAND:
        raise ValueError("Land must be played from hand.")
    if "Land" not in obj.types:
        raise ValueError("Selected card is not a land.")

    game_state.move_object(obj.id, ZONE_BATTLEFIELD)
    obj.was_cast = False
    game_state.turn.land_plays_this_turn += 1
    turn_manager.after_player_action(player_id)


def _validate_cast_timing(game_state, turn_manager, player_id: int, obj) -> None:
    is_instant = "Instant" in obj.types
    has_flash = "Flash" in obj.keywords or ("flash" in (obj.oracle_text or "").lower())
    if not is_instant and not has_flash:
        require_active_player(turn_manager, player_id)
        require_main_phase(game_state)
        require_empty_stack(game_state)
    _require_combat_declarations_done(game_state)


def _validate_ability_timing(game_state, turn_manager, player_id: int, obj, runtime) -> None:
    timing = (runtime.timing or "").lower()
    oracle_text = (obj.oracle_text or "").lower()
    if timing == "sorcery" or "activate only as a sorcery" in oracle_text:
        require_active_player(turn_manager, player_id)
        require_main_phase(game_state)
        require_empty_stack(game_state)
    _require_combat_declarations_done(game_state)


def _require_combat_declarations_done(game_state) -> None:
    step = game_state.turn.step
    combat_state = game_state.turn.combat_state
    if step == Step.DECLARE_ATTACKERS:
        if not combat_state or not combat_state.attackers_declared:
            raise ValueError("Declare attackers before taking other actions.")
    if step == Step.DECLARE_BLOCKERS:
        if not combat_state or not combat_state.blockers_declared:
            raise ValueError("Declare blockers before taking other actions.")




def _check_activation_limit(obj, ability_index: int, runtime) -> None:
    limit = runtime.activation_limit or {}
    scope = limit.get("scope")
    max_uses = limit.get("max")
    if not scope or max_uses is None:
        return
    key = f"{ability_index}:{scope}"
    current = obj.activation_limits.get(key, 0)
    if current >= int(max_uses):
        raise ValueError("Ability activation limit reached.")


def _record_activation_use(obj, ability_index: int, runtime) -> None:
    limit = runtime.activation_limit or {}
    scope = limit.get("scope")
    max_uses = limit.get("max")
    if not scope or max_uses is None:
        return
    key = f"{ability_index}:{scope}"
    obj.activation_limits[key] = obj.activation_limits.get(key, 0) + 1


def _require_tap_summoning_sickness_ok(game_state, obj) -> None:
    if "Creature" not in obj.types:
        return
    if obj.entered_turn == game_state.turn.turn_number and "Haste" not in obj.keywords:
        raise ValueError("Creature has summoning sickness.")


def _commander_tax_preview(game_state, player_id: int, obj) -> int:
    player = game_state.get_player(player_id)
    if obj.id == player.commander_id and obj.zone == ZONE_COMMAND:
        return int(player.commander_tax or 0)
    return 0


def _consume_commander_tax(game_state, player_id: int, obj) -> int:
    player = game_state.get_player(player_id)
    if obj.id == player.commander_id and obj.zone == ZONE_COMMAND:
        return apply_commander_tax(game_state, player_id)
    return 0


def _pay_spell_cost(
    game_state,
    player_id: int,
    obj,
    x_value: int,
    mana_payment: Optional[Dict[str, int]],
    mana_payment_detail: Optional[Dict[str, Any]],
    extra_generic: int = 0,
) -> None:
    cost = parse_mana_cost(obj.mana_cost, x_value=x_value)
    if extra_generic:
        cost.generic += int(extra_generic)
    if mana_payment:
        pay_cost_with_payment(game_state, player_id, cost, mana_payment, mana_payment_detail)
        return
    if not can_pay_cost(game_state.get_player(player_id).mana_pool, cost):
        raise ValueError("Not enough mana to cast spell.")
    pay_cost(game_state, player_id, cost)


def cast_spell(
    game_state,
    turn_manager,
    player_id: int,
    object_id: str,
    x_value: int = 0,
    ability_graph: Optional[dict] = None,
    context: Optional[dict] = None,
    mana_payment: Optional[Dict[str, int]] = None,
    mana_payment_detail: Optional[Dict[str, Any]] = None,
) -> None:
    require_priority(turn_manager, player_id)

    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Card not found.")
    if obj.zone not in (ZONE_HAND, ZONE_COMMAND):
        raise ValueError("Spell must be cast from hand or command zone.")
    if obj.zone == ZONE_COMMAND:
        player = game_state.get_player(player_id)
        if obj.id != player.commander_id:
            raise ValueError("Only commanders can be cast from the command zone.")
    if "Land" in obj.types:
        raise ValueError("Lands cannot be cast as spells.")

    _validate_cast_timing(game_state, turn_manager, player_id, obj)

    if context:
        resolve_context = ResolveContext(**context)
        normalize_targets(game_state, resolve_context)
        validate_targets(game_state, resolve_context)
    validate_enter_choices(ability_graph, context)
    commander_tax = _consume_commander_tax(game_state, player_id, obj)
    _pay_spell_cost(game_state, player_id, obj, x_value, mana_payment, mana_payment_detail, commander_tax)

    # Remove from hand and put on stack
    owner = game_state.get_player(obj.owner_id)
    if obj.id in owner.hand:
        owner.hand.remove(obj.id)
    obj.zone = "stack"
    game_state.clear_prepared_casts_for_object(obj.id)
    obj.was_cast = True
    obj.controller_id = player_id

    destination_zone = ZONE_GRAVEYARD if ("Instant" in obj.types or "Sorcery" in obj.types) else ZONE_BATTLEFIELD
    if ability_graph:
        game_state.stack.push(
            StackItem(
                kind="ability_graph",
                payload={
                    "graph": ability_graph,
                    "context": context or {},
                    "source_object_id": obj.id,
                    "destination_zone": destination_zone,
                },
                controller_id=player_id,
            )
        )
    else:
        game_state.stack.push(
            StackItem(
                kind="spell",
                payload={"object_id": obj.id, "destination_zone": destination_zone, "context": context or {}},
                controller_id=player_id,
            )
        )

    game_state.event_bus.publish(Event(type="spell_cast", payload={"object_id": obj.id, "player_id": player_id}))

    # Reset priority pass state after casting
    turn_manager.after_player_action(player_id)


def prepare_cast(
    game_state,
    turn_manager,
    player_id: int,
    object_id: str,
    x_value: int = 0,
    context: Optional[dict] = None,
) -> Dict[str, Any]:
    require_priority(turn_manager, player_id)

    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Card not found.")
    if obj.zone not in (ZONE_HAND, ZONE_COMMAND):
        raise ValueError("Spell must be cast from hand or command zone.")
    if obj.zone == ZONE_COMMAND:
        player = game_state.get_player(player_id)
        if obj.id != player.commander_id:
            raise ValueError("Only commanders can be cast from the command zone.")
    if "Land" in obj.types:
        raise ValueError("Lands cannot be cast as spells.")

    _validate_cast_timing(game_state, turn_manager, player_id, obj)

    if context:
        resolve_context = ResolveContext(**context)
        validate_targets(game_state, resolve_context)

    cost = parse_mana_cost(obj.mana_cost, x_value=x_value)
    commander_tax = _commander_tax_preview(game_state, player_id, obj)
    if commander_tax:
        cost.generic += int(commander_tax)
    game_state.prepared_casts[player_id] = {
        "object_id": obj.id,
        "x_value": x_value,
        "context": context or {},
        "cost": mana_cost_snapshot(cost),
    }
    return {
        "status": "prepared",
        "cost": mana_cost_snapshot(cost),
    }


def declare_attackers(
    game_state,
    turn_manager,
    player_id: int,
    attackers: List[str],
    defending_player_id: Optional[int],
    defending_object_id: Optional[str] = None,
) -> None:
    require_priority(turn_manager, player_id)
    require_active_player(turn_manager, player_id)
    if game_state.turn.step != Step.DECLARE_ATTACKERS:
        raise ValueError("Not in declare attackers step.")
    if game_state.turn.combat_state and game_state.turn.combat_state.attackers_declared:
        raise ValueError("Attackers have already been declared.")

    defending_object = None
    if defending_object_id:
        defending_object = game_state.objects.get(defending_object_id)
        if not defending_object or defending_object.zone != ZONE_BATTLEFIELD:
            raise ValueError("Defending planeswalker not found on the battlefield.")
        if "Planeswalker" not in defending_object.types:
            raise ValueError("Defending object is not a planeswalker.")
        if defending_player_id is None:
            defending_player_id = defending_object.controller_id
        if defending_object.controller_id != defending_player_id:
            raise ValueError("Defending planeswalker is not controlled by the defending player.")
    if defending_player_id is None:
        active_index = game_state.turn.active_player_index
        defending_index = (active_index + 1) % len(game_state.players)
        defending_player_id = game_state.players[defending_index].id

    combat_state = CombatState(
        attacking_player_id=player_id,
        defending_player_id=defending_player_id,
        defending_object_id=defending_object.id if defending_object else None,
        attackers=[],
        blockers={},
    )

    for obj_id in attackers:
        obj = game_state.objects.get(obj_id)
        if not obj:
            raise ValueError("Attacker not found.")
        if obj.zone != ZONE_BATTLEFIELD or obj.controller_id != player_id:
            raise ValueError("Attacker must be on the battlefield under your control.")
        if "Creature" not in obj.types:
            raise ValueError("Only creatures can attack.")
        if obj.phased_out:
            raise ValueError("Phased out creatures cannot attack.")
        if obj.tapped:
            raise ValueError("Tapped creatures cannot attack.")
        if "Defender" in obj.keywords:
            raise ValueError("Creatures with defender cannot attack.")
        if obj.entered_turn == game_state.turn.turn_number and "Haste" not in obj.keywords:
            raise ValueError("Creature has summoning sickness.")
        obj.is_attacking = True
        if "Vigilance" not in obj.keywords:
            obj.tapped = True
        combat_state.attackers.append(obj.id)

    game_state.turn.combat_state = combat_state
    for attacker_id in attackers:
        game_state.event_bus.publish(Event(type="attacks", payload={"object_id": attacker_id}))
    combat_state.attackers_declared = True
    turn_manager.after_player_action(player_id)


def declare_blockers(
    game_state,
    turn_manager,
    player_id: int,
    blockers: Dict[str, List[str]],
) -> None:
    require_priority(turn_manager, player_id)
    if game_state.turn.step != Step.DECLARE_BLOCKERS:
        raise ValueError("Not in declare blockers step.")

    combat_state = game_state.turn.combat_state
    if not combat_state:
        raise ValueError("No combat state is active.")
    if combat_state.blockers_declared:
        raise ValueError("Blockers have already been declared.")
    if combat_state.combat_damage_resolved:
        raise ValueError("Combat damage has already been assigned.")
    if combat_state.defending_player_id != player_id:
        raise ValueError("Only the defending player may declare blockers.")

    used_blockers: set[str] = set()
    for attacker_id, blocker_ids in blockers.items():
        if attacker_id not in combat_state.attackers:
            raise ValueError("Blockers must target an attacking creature.")
        attacker = game_state.objects.get(attacker_id)
        if not attacker or not attacker.is_attacking:
            raise ValueError("Invalid attacking creature.")
        if "Menace" in attacker.keywords and len(blocker_ids) == 1:
            raise ValueError("Menace requires two or more blockers.")
        if len(blocker_ids) != len(set(blocker_ids)):
            raise ValueError("Duplicate blockers are not allowed.")
        for blocker_id in blocker_ids:
            blocker = game_state.objects.get(blocker_id)
            if not blocker:
                raise ValueError("Blocker not found.")
            if blocker.zone != ZONE_BATTLEFIELD or blocker.controller_id != player_id:
                raise ValueError("Blocker must be on the battlefield under your control.")
            if "Creature" not in blocker.types:
                raise ValueError("Only creatures can block.")
            if blocker.phased_out:
                raise ValueError("Phased out creatures cannot block.")
            if blocker.tapped:
                raise ValueError("Tapped creatures cannot block.")
            if blocker_id in used_blockers:
                raise ValueError("A creature cannot block multiple attackers.")
            if "Flying" in attacker.keywords and not (
                "Flying" in blocker.keywords or "Reach" in blocker.keywords
            ):
                raise ValueError("Only creatures with flying or reach can block a flying creature.")
            if attacker.protections and blocker.colors:
                if any(color in attacker.protections for color in blocker.colors):
                    raise ValueError("Attacker has protection from this blocker.")
            blocker.is_blocking = True
            used_blockers.add(blocker_id)
        combat_state.blockers[attacker_id] = list(blocker_ids)
    game_state.event_bus.publish(Event(type="blocks", payload={"blockers": blockers}))
    combat_state.blockers_declared = True
    turn_manager.after_player_action(player_id)


def assign_combat_damage(
    game_state,
    turn_manager,
    player_id: int,
    damage_assignments: Optional[Dict[str, Dict[str, int]]] = None,
    combat_damage_pass: Optional[str] = None,
) -> None:
    require_priority(turn_manager, player_id)
    if game_state.turn.step != Step.COMBAT_DAMAGE:
        raise ValueError("Not in combat damage step.")

    combat_state = game_state.turn.combat_state
    if not combat_state:
        raise ValueError("No combat state is active.")
    resolve_combat_damage(
        game_state,
        turn_manager,
        player_id,
        damage_assignments=damage_assignments,
        combat_damage_pass=combat_damage_pass,
    )


def activate_mana_ability(game_state, turn_manager, player_id: int, object_id: str) -> None:
    if player_id != turn_manager.priority.current and player_id not in game_state.prepared_casts:
        raise ValueError("Player does not have priority or is not casting a spell.")
    _require_combat_declarations_done(game_state)
    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Permanent not found.")
    if obj.controller_id != player_id:
        raise ValueError("You do not control this permanent.")
    if obj.tapped:
        raise ValueError("Permanent is already tapped.")
    _require_tap_summoning_sickness_ok(game_state, obj)

    mana = produce_mana_for_object(game_state, obj)
    obj.tapped = True
    player = game_state.get_player(player_id)
    for color, amount in mana.items():
        player.mana_pool[color] = player.mana_pool.get(color, 0) + amount
    turn_manager.after_mana_ability(player_id)


def activate_ability(
    game_state,
    turn_manager,
    player_id: int,
    object_id: str,
    ability_index: int = 0,
    context: Optional[dict] = None,
) -> None:
    require_priority(turn_manager, player_id)
    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Permanent not found.")
    if obj.controller_id != player_id:
        raise ValueError("You do not control this permanent.")
    if not obj.ability_graphs:
        raise ValueError("Permanent has no abilities to activate.")
    if ability_index < 0 or ability_index >= len(obj.ability_graphs):
        raise ValueError("Invalid ability index.")

    graph = obj.ability_graphs[ability_index]
    adapter = AbilityGraphRuntimeAdapter(game_state)
    runtime = adapter.build_runtime(graph)
    _validate_ability_timing(game_state, turn_manager, player_id, obj, runtime)
    _check_activation_limit(obj, ability_index, runtime)
    if context:
        resolve_context = ResolveContext(**context)
        if resolve_context.source_id is None:
            resolve_context.source_id = obj.id
        if resolve_context.controller_id is None:
            resolve_context.controller_id = player_id
        normalize_targets(game_state, resolve_context)
        validate_targets(game_state, resolve_context)
    validate_enter_choices(graph, context)
    if runtime.cost:
        if "{T}" in runtime.cost or "Tap" in runtime.cost:
            _require_tap_summoning_sickness_ok(game_state, obj)
            if obj.tapped:
                raise ValueError("Permanent is already tapped.")
            obj.tapped = True
        cost = parse_mana_cost(runtime.cost, x_value=0)
        if not can_pay_cost(game_state.get_player(player_id).mana_pool, cost):
            raise ValueError("Not enough mana to activate ability.")
        pay_cost(game_state, player_id, cost)
    _record_activation_use(obj, ability_index, runtime)

    stacked_context = context or {}
    stacked_context.setdefault("source_id", obj.id)
    stacked_context.setdefault("controller_id", player_id)
    game_state.stack.push(
        StackItem(
            kind="ability_graph",
            payload={
                "graph": graph,
                "context": stacked_context,
                "source_object_id": obj.id,
            },
            controller_id=player_id,
        )
    )
    turn_manager.after_player_action(player_id)

