from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ability_graph import AbilityGraphRuntimeAdapter
from .combat import CombatState
from .damage import apply_damage_to_object, apply_damage_to_player
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
from .zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND
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


def _validate_ability_timing(game_state, turn_manager, player_id: int, obj, runtime) -> None:
    timing = (runtime.timing or "").lower()
    oracle_text = (obj.oracle_text or "").lower()
    if timing == "sorcery" or "activate only as a sorcery" in oracle_text:
        require_active_player(turn_manager, player_id)
        require_main_phase(game_state)
        require_empty_stack(game_state)




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


def _pay_spell_cost(
    game_state,
    player_id: int,
    obj,
    x_value: int,
    mana_payment: Optional[Dict[str, int]],
    mana_payment_detail: Optional[Dict[str, Any]],
) -> None:
    cost = parse_mana_cost(obj.mana_cost, x_value=x_value)
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
    if obj.zone != ZONE_HAND:
        raise ValueError("Spell must be cast from hand.")
    if "Land" in obj.types:
        raise ValueError("Lands cannot be cast as spells.")

    _validate_cast_timing(game_state, turn_manager, player_id, obj)

    if context:
        resolve_context = ResolveContext(**context)
        normalize_targets(game_state, resolve_context)
        validate_targets(game_state, resolve_context)
    validate_enter_choices(ability_graph, context)
    _pay_spell_cost(game_state, player_id, obj, x_value, mana_payment, mana_payment_detail)

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
    if obj.zone != ZONE_HAND:
        raise ValueError("Spell must be cast from hand.")
    if "Land" in obj.types:
        raise ValueError("Lands cannot be cast as spells.")

    _validate_cast_timing(game_state, turn_manager, player_id, obj)

    if context:
        resolve_context = ResolveContext(**context)
        validate_targets(game_state, resolve_context)

    cost = parse_mana_cost(obj.mana_cost, x_value=x_value)
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
) -> None:
    require_priority(turn_manager, player_id)
    require_active_player(turn_manager, player_id)
    if game_state.turn.step != Step.DECLARE_ATTACKERS:
        raise ValueError("Not in declare attackers step.")

    if defending_player_id is None:
        active_index = game_state.turn.active_player_index
        defending_index = (active_index + 1) % len(game_state.players)
        defending_player_id = game_state.players[defending_index].id

    combat_state = CombatState(
        attacking_player_id=player_id,
        defending_player_id=defending_player_id,
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
        if obj.tapped:
            raise ValueError("Tapped creatures cannot attack.")
        if obj.entered_turn == game_state.turn.turn_number and "Haste" not in obj.keywords:
            raise ValueError("Creature has summoning sickness.")
        obj.is_attacking = True
        if "Vigilance" not in obj.keywords:
            obj.tapped = True
        combat_state.attackers.append(obj.id)

    game_state.turn.combat_state = combat_state
    for attacker_id in attackers:
        game_state.event_bus.publish(Event(type="attacks", payload={"object_id": attacker_id}))
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
    if combat_state.defending_player_id != player_id:
        raise ValueError("Only the defending player may declare blockers.")

    for attacker_id, blocker_ids in blockers.items():
        if attacker_id not in combat_state.attackers:
            raise ValueError("Blockers must target an attacking creature.")
        attacker = game_state.objects.get(attacker_id)
        if not attacker or not attacker.is_attacking:
            raise ValueError("Invalid attacking creature.")
        for blocker_id in blocker_ids:
            blocker = game_state.objects.get(blocker_id)
            if not blocker:
                raise ValueError("Blocker not found.")
            if blocker.zone != ZONE_BATTLEFIELD or blocker.controller_id != player_id:
                raise ValueError("Blocker must be on the battlefield under your control.")
            if "Creature" not in blocker.types:
                raise ValueError("Only creatures can block.")
            if blocker.tapped:
                raise ValueError("Tapped creatures cannot block.")
            if "Flying" in attacker.keywords and not (
                "Flying" in blocker.keywords or "Reach" in blocker.keywords
            ):
                raise ValueError("Only creatures with flying or reach can block a flying creature.")
            blocker.is_blocking = True
        combat_state.blockers[attacker_id] = list(blocker_ids)
    game_state.event_bus.publish(Event(type="blocks", payload={"blockers": blockers}))
    turn_manager.after_player_action(player_id)


def assign_combat_damage(
    game_state,
    turn_manager,
    player_id: int,
    damage_assignments: Optional[Dict[str, Dict[str, int]]] = None,
) -> None:
    require_priority(turn_manager, player_id)
    if game_state.turn.step != Step.COMBAT_DAMAGE:
        raise ValueError("Not in combat damage step.")

    combat_state = game_state.turn.combat_state
    if not combat_state:
        raise ValueError("No combat state is active.")

    if damage_assignments:
        for attacker_id, assignments in damage_assignments.items():
            attacker = game_state.objects.get(attacker_id)
            if not attacker:
                continue
            for target_id, amount in assignments.items():
                if target_id.startswith("player:"):
                    player_target_id = int(target_id.split(":", 1)[1])
                    player = game_state.get_player(player_target_id)
                    player.life -= int(amount)
                elif target_id == "player":
                    player = game_state.get_player(combat_state.defending_player_id)
                    player.life -= int(amount)
                else:
                    target = game_state.objects.get(target_id)
                    if target:
                        target.damage += int(amount)
        return

    def get_power(obj) -> int:
        return int(obj.power or 0)

    def has_keyword(obj, keyword: str) -> bool:
        return keyword in obj.keywords

    def is_alive(obj) -> bool:
        return obj.zone == ZONE_BATTLEFIELD

    def can_deal_in_first_strike(obj) -> bool:
        return has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")

    def can_deal_in_second_strike(obj) -> bool:
        return not has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")

    def lethal_damage_required(defender, deathtouch: bool) -> int:
        if defender.toughness is None:
            return 0
        if deathtouch:
            return 1
        return max(0, int(defender.toughness) - int(defender.damage or 0))

    def deal_to_blockers(attacker, blockers):
        remaining = get_power(attacker)
        if remaining <= 0:
            return
        deathtouch = has_keyword(attacker, "Deathtouch")
        for blocker in blockers:
            if remaining <= 0:
                break
            lethal = lethal_damage_required(blocker, deathtouch)
            assign = remaining if lethal == 0 else min(remaining, lethal)
            if assign > 0:
                apply_damage_to_object(game_state, attacker, blocker, assign)
            remaining -= assign
        if remaining > 0 and has_keyword(attacker, "Trample"):
            apply_damage_to_player(game_state, attacker, combat_state.defending_player_id, remaining)

    def deal_blocker_damage(attacker, blockers):
        for blocker in blockers:
            if get_power(blocker) <= 0:
                continue
            apply_damage_to_object(game_state, blocker, attacker, get_power(blocker))

    def resolve_combat_pass(first_strike_pass: bool):
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            blockers = [
                game_state.objects.get(blocker_id)
                for blocker_id in combat_state.blockers.get(attacker_id, [])
            ]
            blockers = [b for b in blockers if b and is_alive(b) and b.is_blocking]

            attacker_can_deal = can_deal_in_first_strike(attacker) if first_strike_pass else can_deal_in_second_strike(attacker)
            eligible_blockers = [
                b for b in blockers
                if (can_deal_in_first_strike(b) if first_strike_pass else can_deal_in_second_strike(b))
            ]

            if not blockers:
                if attacker_can_deal:
                    apply_damage_to_player(game_state, attacker, combat_state.defending_player_id, get_power(attacker))
                continue

            if attacker_can_deal:
                deal_to_blockers(attacker, blockers)
            if eligible_blockers and is_alive(attacker):
                deal_blocker_damage(attacker, eligible_blockers)

        apply_state_based_actions(game_state)

    has_first_strike_combat = False
    for attacker_id in combat_state.attackers:
        attacker = game_state.objects.get(attacker_id)
        if attacker and (has_keyword(attacker, "First strike") or has_keyword(attacker, "Double strike")):
            has_first_strike_combat = True
            break
        for blocker_id in combat_state.blockers.get(attacker_id, []):
            blocker = game_state.objects.get(blocker_id)
            if blocker and (has_keyword(blocker, "First strike") or has_keyword(blocker, "Double strike")):
                has_first_strike_combat = True
                break
        if has_first_strike_combat:
            break

    if has_first_strike_combat:
        resolve_combat_pass(first_strike_pass=True)
        resolve_combat_pass(first_strike_pass=False)
    else:
        resolve_combat_pass(first_strike_pass=False)
    turn_manager.after_player_action(player_id)


def activate_mana_ability(game_state, turn_manager, player_id: int, object_id: str) -> None:
    if player_id != turn_manager.priority.current and player_id not in game_state.prepared_casts:
        raise ValueError("Player does not have priority or is not casting a spell.")
    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Permanent not found.")
    if obj.controller_id != player_id:
        raise ValueError("You do not control this permanent.")
    if obj.tapped:
        raise ValueError("Permanent is already tapped.")

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
    if runtime.cost:
        if "{T}" in runtime.cost or "Tap" in runtime.cost:
            if obj.tapped:
                raise ValueError("Permanent is already tapped.")
            obj.tapped = True
        cost = parse_mana_cost(runtime.cost, x_value=0)
        if not can_pay_cost(game_state.get_player(player_id).mana_pool, cost):
            raise ValueError("Not enough mana to activate ability.")
        pay_cost(game_state, player_id, cost)
    _record_activation_use(obj, ability_index, runtime)

    game_state.stack.push(
        StackItem(
            kind="ability_graph",
            payload={
                "graph": graph,
                "context": {
                    "source_id": obj.id,
                    "controller_id": player_id,
                },
                "source_object_id": obj.id,
            },
            controller_id=player_id,
        )
    )
    turn_manager.after_player_action(player_id)

