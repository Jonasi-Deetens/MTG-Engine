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
from .state import ResolveContext, GameObject
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

    def _redirect_effects(source_id: str) -> List[Dict[str, Any]]:
        return [
            effect
            for effect in list(game_state.replacement_effects)
            if effect.get("type") == "redirect_damage" and effect.get("source") == source_id
        ]

    def _prevent_effects_for_object(obj: GameObject) -> List[Dict[str, Any]]:
        return [effect for effect in obj.temporary_effects if effect.get("prevent_damage") is not None]

    def _prevent_effects_for_player(target_player_id: int) -> List[Dict[str, Any]]:
        return [
            effect
            for effect in list(game_state.replacement_effects)
            if effect.get("type") == "prevent_damage" and effect.get("player_id") == target_player_id
        ]

    def _requires_choice(source_id: str, target_key: str) -> bool:
        return target_key not in game_state.replacement_choices

    def _register_event_choice(source_id: str, target_key: str, target_obj: Optional[GameObject], player_target_id: Optional[int]) -> bool:
        redirect_effects = _redirect_effects(source_id)
        if target_obj:
            prevent_effects = _prevent_effects_for_object(target_obj)
        else:
            prevent_effects = _prevent_effects_for_player(player_target_id) if player_target_id is not None else []
        if len(redirect_effects) + len(prevent_effects) > 1:
            return _requires_choice(source_id, target_key)
        return False

    def get_power(obj) -> int:
        return int(obj.power or 0)

    def has_keyword(obj, keyword: str) -> bool:
        return keyword in obj.keywords

    def is_alive(obj) -> bool:
        return obj.zone == ZONE_BATTLEFIELD

    def lethal_damage_required(defender, deathtouch: bool) -> int:
        if defender.toughness is None:
            return 0
        if deathtouch:
            return 1
        return max(0, int(defender.toughness) - int(defender.damage or 0))

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

    if combat_damage_pass not in (None, "first_strike", "regular"):
        raise ValueError("Invalid combat damage pass.")
    if has_first_strike_combat:
        if combat_damage_pass == "first_strike" and combat_state.first_strike_resolved:
            raise ValueError("First strike combat damage already assigned.")
        if combat_damage_pass == "regular" and not combat_state.first_strike_resolved:
            raise ValueError("First strike combat damage must resolve first.")
        if combat_damage_pass is None and damage_assignments:
            raise ValueError("Combat damage pass is required with first/double strike.")
        if combat_damage_pass is None and combat_state.first_strike_resolved:
            raise ValueError("Combat damage pass is required with first/double strike.")
    else:
        if combat_damage_pass == "first_strike":
            raise ValueError("First strike combat damage does not apply.")

    def is_eligible_for_pass(obj) -> bool:
        if combat_damage_pass == "first_strike":
            return has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")
        if combat_damage_pass == "regular":
            return not has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")
        return True

    def _validate_manual_assignments(assignments: Dict[str, Dict[str, int]]) -> None:
        if not combat_state:
            raise ValueError("No combat state is active.")
        if not assignments:
            raise ValueError("No damage assignments provided.")
        valid_attackers = set(combat_state.attackers)
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            if get_power(attacker) <= 0:
                continue
            if not is_eligible_for_pass(attacker):
                continue
            if attacker_id not in assignments:
                raise ValueError("Missing combat damage assignment.")
        for source_id, targets in assignments.items():
            if source_id not in valid_attackers:
                raise ValueError("Invalid combat damage source.")
            source = game_state.objects.get(source_id)
            if not source or source.zone != ZONE_BATTLEFIELD:
                raise ValueError("Invalid combat damage source.")
            if not is_eligible_for_pass(source):
                raise ValueError("Combat damage source is not eligible this pass.")
            if not targets:
                raise ValueError("Damage assignments missing targets.")
            blocker_ids = combat_state.blockers.get(source_id, [])
            has_player_assignment = False
            total = 0
            for target_id, amount in targets.items():
                try:
                    amt = int(amount)
                except (TypeError, ValueError):
                    raise ValueError("Invalid damage amount.")
                if amt < 0:
                    raise ValueError("Damage amount must be non-negative.")
                if target_id == "player":
                    if combat_state.defending_player_id is None:
                        raise ValueError("No defending player for combat damage.")
                    if combat_state.defending_object_id is not None:
                        raise ValueError("Combat damage must be assigned to the defending planeswalker.")
                    has_player_assignment = True
                elif target_id == "defender":
                    if combat_state.defending_object_id is None:
                        raise ValueError("No defending planeswalker for combat damage.")
                    has_player_assignment = True
                elif target_id.startswith("player:"):
                    player_target_id = int(target_id.split(":", 1)[1])
                    if player_target_id != combat_state.defending_player_id:
                        raise ValueError("Combat damage can only be assigned to the defending player.")
                    if combat_state.defending_object_id is not None:
                        raise ValueError("Combat damage must be assigned to the defending planeswalker.")
                    has_player_assignment = True
                elif target_id.startswith("planeswalker:"):
                    planeswalker_id = target_id.split(":", 1)[1]
                    if combat_state.defending_object_id != planeswalker_id:
                        raise ValueError("Combat damage can only be assigned to the defending planeswalker.")
                    has_player_assignment = True
                else:
                    if target_id not in combat_state.blockers.get(source_id, []):
                        raise ValueError("Combat damage assigned to an invalid blocker.")
                total += amt
            source_power = int(source.power or 0)
            if total > source_power:
                raise ValueError("Assigned damage exceeds power.")
            if total < source_power and "Trample" not in source.keywords:
                raise ValueError("Assigned damage must equal power without trample.")
            if blocker_ids and has_player_assignment and "Trample" not in source.keywords:
                raise ValueError("Combat damage to player requires trample.")
            if combat_state.blockers.get(source_id):
                order = combat_state.blockers.get(source_id, [])
                deathtouch = "Deathtouch" in source.keywords
                remaining = source_power
                for blocker_id in order:
                    if remaining <= 0:
                        break
                    blocker = game_state.objects.get(blocker_id)
                    if not blocker:
                        continue
                    assign = int(targets.get(blocker_id, 0))
                    lethal = lethal_damage_required(blocker, deathtouch)
                    if assign < min(remaining, lethal):
                        raise ValueError("Damage must be assigned to blockers in lethal order.")
                    remaining -= assign
                if remaining > 0 and "Trample" not in source.keywords:
                    raise ValueError("Unassigned combat damage without trample.")

    if damage_assignments:
        _validate_manual_assignments(damage_assignments)
        missing_choices: List[str] = []
        used_event_keys: set[str] = set()
        for source_id, assignments in damage_assignments.items():
            source = game_state.objects.get(source_id)
            if not source:
                continue
            for target_id, amount in assignments.items():
                if int(amount) <= 0:
                    continue
                if target_id.startswith("player:"):
                    player_target_id = int(target_id.split(":", 1)[1])
                    event_key = f"damage:event:{source_id}:player:{player_target_id}"
                    if _register_event_choice(source_id, event_key, None, player_target_id):
                        missing_choices.append(event_key)
                    used_event_keys.add(event_key)
                elif target_id == "player":
                    event_key = f"damage:event:{source_id}:player:{combat_state.defending_player_id}"
                    if _register_event_choice(source_id, event_key, None, combat_state.defending_player_id):
                        missing_choices.append(event_key)
                    used_event_keys.add(event_key)
                elif target_id == "defender":
                    planeswalker_id = combat_state.defending_object_id
                    if planeswalker_id:
                        target = game_state.objects.get(planeswalker_id)
                        event_key = f"damage:event:{source_id}:object:{planeswalker_id}"
                        if target and _register_event_choice(source_id, event_key, target, None):
                            missing_choices.append(event_key)
                        used_event_keys.add(event_key)
                elif target_id.startswith("planeswalker:"):
                    planeswalker_id = target_id.split(":", 1)[1]
                    target = game_state.objects.get(planeswalker_id)
                    event_key = f"damage:event:{source_id}:object:{planeswalker_id}"
                    if target and _register_event_choice(source_id, event_key, target, None):
                        missing_choices.append(event_key)
                    used_event_keys.add(event_key)
                else:
                    target = game_state.objects.get(target_id)
                    if target:
                        event_key = f"damage:event:{source_id}:object:{target_id}"
                        if _register_event_choice(source_id, event_key, target, None):
                            missing_choices.append(event_key)
                        used_event_keys.add(event_key)
        if missing_choices:
            raise ValueError("Damage replacement choice required.")
        for source_id, assignments in damage_assignments.items():
            source = game_state.objects.get(source_id)
            if not source:
                continue
            for target_id, amount in assignments.items():
                if int(amount) <= 0:
                    continue
                if target_id.startswith("player:"):
                    player_target_id = int(target_id.split(":", 1)[1])
                    apply_damage_to_player(game_state, source, player_target_id, int(amount))
                elif target_id == "player":
                    apply_damage_to_player(game_state, source, combat_state.defending_player_id, int(amount))
                elif target_id == "defender":
                    planeswalker_id = combat_state.defending_object_id
                    target = game_state.objects.get(planeswalker_id) if planeswalker_id else None
                    if target:
                        apply_damage_to_object(game_state, source, target, int(amount))
                elif target_id.startswith("planeswalker:"):
                    planeswalker_id = target_id.split(":", 1)[1]
                    target = game_state.objects.get(planeswalker_id)
                    if target:
                        apply_damage_to_object(game_state, source, target, int(amount))
                else:
                    target = game_state.objects.get(target_id)
                    if target:
                        apply_damage_to_object(game_state, source, target, int(amount))
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            blockers = [
                game_state.objects.get(blocker_id)
                for blocker_id in combat_state.blockers.get(attacker_id, [])
            ]
            blockers = [b for b in blockers if b and is_alive(b) and b.is_blocking and is_eligible_for_pass(b)]
            for blocker in blockers:
                if get_power(blocker) <= 0:
                    continue
                used_event_keys.add(f"damage:event:{blocker.id}:object:{attacker_id}")
                apply_damage_to_object(game_state, blocker, attacker, get_power(blocker))
        apply_state_based_actions(game_state)
        for key in used_event_keys:
            game_state.replacement_choices.pop(key, None)
        if has_first_strike_combat:
            if combat_damage_pass == "first_strike":
                combat_state.first_strike_resolved = True
            elif combat_damage_pass == "regular":
                combat_state.combat_damage_resolved = True
        else:
            combat_state.combat_damage_resolved = True
        return

    def can_deal_in_first_strike(obj) -> bool:
        return has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")

    def can_deal_in_second_strike(obj) -> bool:
        return not has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")

    def register_combat_event_choice(
        source_obj: GameObject,
        target_obj: Optional[GameObject],
        player_target_id: Optional[int],
        event_key: str,
    ) -> bool:
        return _register_event_choice(source_obj.id, event_key, target_obj, player_target_id)

    def apply_damage_to_defender(attacker: GameObject, amount: int, used_event_keys: Optional[set[str]] = None) -> None:
        if combat_state.defending_object_id:
            defender = game_state.objects.get(combat_state.defending_object_id)
            if defender:
                if used_event_keys is not None:
                    used_event_keys.add(f"damage:event:{attacker.id}:object:{defender.id}")
                apply_damage_to_object(game_state, attacker, defender, amount)
            return
        if used_event_keys is not None:
            used_event_keys.add(f"damage:event:{attacker.id}:player:{combat_state.defending_player_id}")
        apply_damage_to_player(game_state, attacker, combat_state.defending_player_id, amount)

    def deal_to_blockers(attacker, blockers, used_event_keys: Optional[set[str]] = None):
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
                if used_event_keys is not None:
                    used_event_keys.add(f"damage:event:{attacker.id}:object:{blocker.id}")
                apply_damage_to_object(game_state, attacker, blocker, assign)
            remaining -= assign
        if remaining > 0 and has_keyword(attacker, "Trample"):
            apply_damage_to_defender(attacker, remaining, used_event_keys)

    def deal_blocker_damage(attacker, blockers, used_event_keys: Optional[set[str]] = None):
        for blocker in blockers:
            if get_power(blocker) <= 0:
                continue
            if used_event_keys is not None:
                used_event_keys.add(f"damage:event:{blocker.id}:object:{attacker.id}")
            apply_damage_to_object(game_state, blocker, attacker, get_power(blocker))

    def resolve_combat_pass(first_strike_pass: bool, used_event_keys: Optional[set[str]] = None):
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
                    apply_damage_to_defender(attacker, get_power(attacker), used_event_keys)
                continue

            if attacker_can_deal:
                deal_to_blockers(attacker, blockers, used_event_keys)
            if eligible_blockers and is_alive(attacker):
                deal_blocker_damage(attacker, eligible_blockers, used_event_keys)

        apply_state_based_actions(game_state)

    def can_deal_in_first_strike(obj) -> bool:
        return has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")

    def can_deal_in_second_strike(obj) -> bool:
        return not has_keyword(obj, "First strike") or has_keyword(obj, "Double strike")


    def _collect_missing_combat_choices() -> List[str]:
        missing: List[str] = []
        for attacker_id in combat_state.attackers:
            attacker = game_state.objects.get(attacker_id)
            if not attacker or not is_alive(attacker) or not attacker.is_attacking:
                continue
            if not is_eligible_for_pass(attacker):
                continue
            blockers = [
                game_state.objects.get(blocker_id)
                for blocker_id in combat_state.blockers.get(attacker_id, [])
            ]
            blockers = [b for b in blockers if b and is_alive(b) and b.is_blocking and is_eligible_for_pass(b)]
            if not blockers:
                if combat_state.defending_object_id:
                    defender = game_state.objects.get(combat_state.defending_object_id)
                    if defender:
                        event_key = f"damage:event:{attacker.id}:object:{defender.id}"
                        if register_combat_event_choice(attacker, defender, None, event_key):
                            missing.append(event_key)
                else:
                    event_key = f"damage:event:{attacker.id}:player:{combat_state.defending_player_id}"
                    if register_combat_event_choice(attacker, None, combat_state.defending_player_id, event_key):
                        missing.append(event_key)
                continue
            remaining = get_power(attacker)
            if remaining > 0:
                deathtouch = has_keyword(attacker, "Deathtouch")
                for blocker in blockers:
                    if remaining <= 0:
                        break
                    lethal = lethal_damage_required(blocker, deathtouch)
                    assign = remaining if lethal == 0 else min(remaining, lethal)
                    if assign > 0:
                        event_key = f"damage:event:{attacker.id}:object:{blocker.id}"
                        if register_combat_event_choice(attacker, blocker, None, event_key):
                            missing.append(event_key)
                    remaining -= assign
                if remaining > 0 and has_keyword(attacker, "Trample"):
                    if combat_state.defending_object_id:
                        defender = game_state.objects.get(combat_state.defending_object_id)
                        if defender:
                            event_key = f"damage:event:{attacker.id}:object:{defender.id}"
                            if register_combat_event_choice(attacker, defender, None, event_key):
                                missing.append(event_key)
                    else:
                        event_key = f"damage:event:{attacker.id}:player:{combat_state.defending_player_id}"
                        if register_combat_event_choice(attacker, None, combat_state.defending_player_id, event_key):
                            missing.append(event_key)
            for blocker in blockers:
                if get_power(blocker) <= 0:
                    continue
                event_key = f"damage:event:{blocker.id}:object:{attacker.id}"
                if register_combat_event_choice(blocker, attacker, None, event_key):
                    missing.append(event_key)
        return missing

    if _collect_missing_combat_choices():
        raise ValueError("Damage replacement choice required.")
    used_event_keys: set[str] = set()
    if combat_damage_pass == "first_strike":
        resolve_combat_pass(first_strike_pass=True, used_event_keys=used_event_keys)
        combat_state.first_strike_resolved = True
    elif combat_damage_pass == "regular":
        resolve_combat_pass(first_strike_pass=False, used_event_keys=used_event_keys)
        combat_state.combat_damage_resolved = True
    else:
        if has_first_strike_combat:
            resolve_combat_pass(first_strike_pass=True, used_event_keys=used_event_keys)
            resolve_combat_pass(first_strike_pass=False, used_event_keys=used_event_keys)
            combat_state.first_strike_resolved = True
            combat_state.combat_damage_resolved = True
        else:
            resolve_combat_pass(first_strike_pass=False, used_event_keys=used_event_keys)
            combat_state.combat_damage_resolved = True
    for key in used_event_keys:
        game_state.replacement_choices.pop(key, None)
    turn_manager.after_player_action(player_id)


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

