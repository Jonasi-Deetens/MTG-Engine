from __future__ import annotations

from typing import Any, Dict, List, Optional

from .combat import CombatState
from .combat_damage import resolve_combat_damage
from .commander import apply_commander_tax
from .mana import (
    can_pay_cost,
    mana_cost_snapshot,
    parse_mana_cost,
    pay_cost,
    pay_cost_with_payment,
)
from .cost_modifiers import apply_cast_cost_modifiers
from .costs import (
    pay_activation_costs,
    pay_costs,
)
from .stack import StackItem
from .targets import enforce_ward_payment, normalize_targets, validate_targets
from .turn import Phase, Step
from .zones import ZONE_BATTLEFIELD, ZONE_COMMAND, ZONE_EXILE, ZONE_GRAVEYARD, ZONE_HAND
from .events import Event
from .state import ResolveContext
from .choices import validate_enter_choices_effect_graph, validate_modal_choices_effect_graph
from .effects.effect_resolver import EffectGraphResolver
from .optional_costs import (
    extract_additional_costs_from_graph,
    extract_optional_costs_from_graph,
    resolve_alternative_cost_from_graph,
)
from .conspire import apply_conspire_cost
from .splice import apply_splice_choices
from .stack_helpers import push_spell_copies


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
    has_flash = "Flash" in obj.keywords
    if not is_instant and not has_flash:
        require_active_player(turn_manager, player_id)
        require_main_phase(game_state)
        require_empty_stack(game_state)
    _require_combat_declarations_done(game_state)


def _validate_ability_timing(game_state, turn_manager, player_id: int, obj, timing: Optional[str]) -> None:
    timing = (timing or "").lower()
    if timing == "sorcery":
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


def _publish_becomes_target(game_state, source_id: Optional[str], resolve_context: Optional[ResolveContext]) -> None:
    if not source_id or not resolve_context:
        return
    targets = set()
    target_id = resolve_context.targets.get("target")
    if target_id:
        targets.add(target_id)
    target_list = resolve_context.targets.get("targets") if isinstance(resolve_context.targets.get("targets"), list) else []
    for obj_id in target_list:
        targets.add(obj_id)
    for obj_id in targets:
        if obj_id in game_state.objects:
            game_state.event_bus.publish(Event(
                type="becomes_target",
                payload={"object_id": obj_id, "source_id": source_id},
            ))




def _check_activation_limit(obj, ability_index: int, limit: Optional[Dict[str, Any]]) -> None:
    limit = limit or {}
    scope = limit.get("scope")
    max_uses = limit.get("max")
    if not scope or max_uses is None:
        return
    key = f"{ability_index}:{scope}"
    current = obj.activation_limits.get(key, 0)
    if current >= int(max_uses):
        raise ValueError("Ability activation limit reached.")


def _record_activation_use(obj, ability_index: int, limit: Optional[Dict[str, Any]]) -> None:
    limit = limit or {}
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
    cost_override: Optional[str] = None,
    free_cast: bool = False,
    resolve_context: Optional[ResolveContext] = None,
) -> None:
    cost_text = None if free_cast else (cost_override or obj.mana_cost)
    cost = parse_mana_cost(cost_text, x_value=x_value)
    if extra_generic:
        cost.generic += int(extra_generic)
    cost = apply_cast_cost_modifiers(game_state, player_id, obj, cost, resolve_context)
    if mana_payment:
        pay_cost_with_payment(game_state, player_id, cost, mana_payment, mana_payment_detail)
        return
    if not can_pay_cost(game_state.get_player(player_id).mana_pool, cost):
        raise ValueError("Not enough mana to cast spell.")
    pay_cost(game_state, player_id, cost)


def _resolve_alternative_cost(
    effect_graph: Optional[dict],
    context: Optional[ResolveContext],
) -> tuple[Optional[str], bool, Optional[str], List[Dict[str, Any]]]:
    return resolve_alternative_cost_from_graph(effect_graph, context)


def cast_spell(
    game_state,
    turn_manager,
    player_id: int,
    object_id: str,
    x_value: int = 0,
    effect_graph: Optional[dict] = None,
    context: Optional[dict] = None,
    mana_payment: Optional[Dict[str, int]] = None,
    mana_payment_detail: Optional[Dict[str, Any]] = None,
) -> None:
    require_priority(turn_manager, player_id)

    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Card not found.")
    if obj.zone not in (ZONE_HAND, ZONE_COMMAND):
        resolve_context = ResolveContext(**context) if context else None
        _, _, alt_tag, _ = _resolve_alternative_cost(effect_graph, resolve_context)
        if obj.zone == ZONE_GRAVEYARD and alt_tag and alt_tag.split(":", 1)[0] in ("flashback", "jump-start", "escape"):
            pass
        else:
            raise ValueError("Spell must be cast from hand or command zone.")
    if obj.zone == ZONE_COMMAND:
        player = game_state.get_player(player_id)
        if obj.id != player.commander_id:
            raise ValueError("Only commanders can be cast from the command zone.")
    if "Land" in obj.types:
        raise ValueError("Lands cannot be cast as spells.")

    _validate_cast_timing(game_state, turn_manager, player_id, obj)

    resolve_context = None
    if context:
        resolve_context = ResolveContext(**context)
        if resolve_context.source_id is None:
            resolve_context.source_id = obj.id
        if resolve_context.controller_id is None:
            resolve_context.controller_id = player_id
        normalize_targets(game_state, resolve_context)
        validate_targets(game_state, resolve_context)
        enforce_ward_payment(game_state, resolve_context)
    validate_enter_choices_effect_graph(effect_graph, context)
    if effect_graph and resolve_context and isinstance(resolve_context.choices, dict):
        optional_costs = extract_optional_costs_from_graph(effect_graph)
        optional_tags = {entry.get("tag"): entry for entry in optional_costs if entry.get("tag")}
        selected_optional = resolve_context.choices.get("optional_costs")
        if isinstance(selected_optional, dict):
            for tag, count in selected_optional.items():
                if not tag or not count:
                    continue
                entry = optional_tags.get(tag)
                if entry and entry.get("kind") == "entwine":
                    modal = effect_graph.get("modal") if isinstance(effect_graph, dict) else None
                    if modal and isinstance(modal.get("modes"), list):
                        resolve_context.choices.setdefault(
                            "chosen_modes",
                            [mode.get("id") for mode in modal.get("modes") if isinstance(mode, dict) and mode.get("id")]
                        )
                        resolve_context.choices["entwine"] = True
                    break
    validate_modal_choices_effect_graph(effect_graph, resolve_context.__dict__ if resolve_context else context)
    cost_override, free_cast, alt_tag, alt_extra_costs = _resolve_alternative_cost(effect_graph, resolve_context)
    additional_costs = extract_additional_costs_from_graph(effect_graph) if effect_graph else []
    optional_costs = extract_optional_costs_from_graph(effect_graph) if effect_graph else []
    copy_count = 0
    if optional_costs and resolve_context:
        choices = resolve_context.choices or {}
        resolve_context.choices = choices
        selected = choices.get("optional_costs") if isinstance(choices, dict) else None
        selected_counts: Dict[str, int] = {}
        if isinstance(selected, dict):
            for key, value in selected.items():
                if isinstance(value, int):
                    selected_counts[key] = value
                elif isinstance(value, bool):
                    selected_counts[key] = 1 if value else 0
        kicker_count = 0
        buyback_paid = False
        conspire_paid = False
        expanded_costs: List[Dict[str, Any]] = []
        available_tags = {entry.get("tag") for entry in optional_costs if entry.get("tag")}
        invalid_tags = [tag for tag, count in selected_counts.items() if tag not in available_tags and count > 0]
        if invalid_tags:
            raise ValueError("Invalid optional cost selection.")
        for entry in optional_costs:
            tag = entry.get("tag")
            if not tag or tag not in selected_counts:
                continue
            count = selected_counts.get(tag, 0)
            if count <= 0:
                continue
            repeatable = bool(entry.get("repeatable"))
            if not repeatable:
                count = 1
            option_costs = entry.get("costs") if isinstance(entry.get("costs"), list) else []
            for _ in range(count):
                expanded_costs.extend(option_costs)
            if entry.get("kind") in ("kicker", "multikicker"):
                kicker_count += count
            if entry.get("kind") == "buyback":
                buyback_paid = True
            if entry.get("kind") == "replicate":
                copy_count += count
                choices["replicate_count"] = copy_count
            if entry.get("kind") == "conspire":
                conspire_paid = True
        if expanded_costs:
            pay_costs(
                game_state,
                player_id,
                obj,
                expanded_costs,
                resolve_context.choices if resolve_context else {},
                "optional_cost_payments",
            )
        if kicker_count > 0:
            choices["kicked"] = True
            choices["kicker_count"] = kicker_count
        if buyback_paid:
            choices["buyback_paid"] = True
        if any(entry.get("kind") == "entwine" and selected_counts.get(entry.get("tag"), 0) > 0 for entry in optional_costs):
            choices["entwine"] = True
        if conspire_paid:
            choices["conspired"] = True
            copy_count += 1
    if alt_extra_costs:
        pay_costs(
            game_state,
            player_id,
            obj,
            alt_extra_costs,
            resolve_context.choices if resolve_context else {},
            "alternative_cost_payments",
        )
    if additional_costs:
        pay_costs(
            game_state,
            player_id,
            obj,
            additional_costs,
            resolve_context.choices if resolve_context else {},
            "additional_cost_payments",
        )
    if resolve_context:
        apply_splice_choices(
            game_state,
            player_id,
            effect_graph,
            resolve_context,
        )
        if resolve_context.choices.get("conspired"):
            apply_conspire_cost(game_state, player_id, obj, resolve_context.choices.get("conspire_taps"))
    commander_tax = _consume_commander_tax(game_state, player_id, obj)
    _pay_spell_cost(
        game_state,
        player_id,
        obj,
        x_value,
        mana_payment,
        mana_payment_detail,
        commander_tax,
        cost_override=cost_override,
        free_cast=free_cast,
        resolve_context=resolve_context,
    )

    # Remove from hand and put on stack
    owner = game_state.get_player(obj.owner_id)
    if obj.id in owner.hand:
        owner.hand.remove(obj.id)
    if obj.id in owner.graveyard:
        owner.graveyard.remove(obj.id)
    obj.zone = "stack"
    game_state.clear_prepared_casts_for_object(obj.id)
    obj.was_cast = True
    obj.controller_id = player_id

    destination_zone = ZONE_GRAVEYARD if ("Instant" in obj.types or "Sorcery" in obj.types) else ZONE_BATTLEFIELD
    if alt_tag and alt_tag.split(":", 1)[0] in ("flashback", "jump-start", "escape"):
        destination_zone = ZONE_EXILE
    # Use the processed resolve_context which includes choices like alternative_cost_tag
    stacked_context = resolve_context.__dict__ if resolve_context else (context or {})
    if effect_graph:
        effect_id = effect_graph.get("id") or "spell-0"
        game_state.stack.push(
            StackItem(
                kind="effect_graph",
                payload={
                    "graph": effect_graph,
                    "context": stacked_context,
                    "source_object_id": obj.id,
                    "destination_zone": destination_zone,
                    "effect_id": effect_id,
                },
                controller_id=player_id,
            )
        )
        message = f"[graph] cast_spell pushed effect_graph source={obj.id} effect_id={effect_id}"
        game_state.log(message)
        print(message, flush=True)
    else:
        game_state.stack.push(
            StackItem(
                kind="spell",
                payload={"object_id": obj.id, "destination_zone": destination_zone, "context": stacked_context},
                controller_id=player_id,
            )
        )
        message = f"[graph] cast_spell pushed spell source={obj.id}"
        game_state.log(message)
        print(message, flush=True)
    if copy_count > 0:
        push_spell_copies(
            game_state,
            obj.id,
            effect_graph,
            stacked_context,
            player_id,
            copy_count,
            resolve_context.choices.get("copy_targets_list") if resolve_context else None,
        )

    _publish_becomes_target(game_state, obj.id, resolve_context)
    game_state.event_bus.publish(Event(type="spell_cast", payload={"object_id": obj.id, "player_id": player_id}))

    # Reset priority pass state after casting
    turn_manager.after_player_action(player_id)


def prepare_cast(
    game_state,
    turn_manager,
    player_id: int,
    object_id: str,
    x_value: int = 0,
    effect_graph: Optional[dict] = None,
    context: Optional[dict] = None,
) -> Dict[str, Any]:
    require_priority(turn_manager, player_id)

    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Card not found.")
    if obj.zone not in (ZONE_HAND, ZONE_COMMAND):
        resolve_context = ResolveContext(**context) if context else None
        _, _, alt_tag, _ = _resolve_alternative_cost(effect_graph, resolve_context)
        if obj.zone == ZONE_GRAVEYARD and alt_tag and alt_tag.split(":", 1)[0] in ("flashback", "jump-start", "escape"):
            pass
        else:
            raise ValueError("Spell must be cast from hand or command zone.")
    if obj.zone == ZONE_COMMAND:
        player = game_state.get_player(player_id)
        if obj.id != player.commander_id:
            raise ValueError("Only commanders can be cast from the command zone.")
    if "Land" in obj.types:
        raise ValueError("Lands cannot be cast as spells.")

    _validate_cast_timing(game_state, turn_manager, player_id, obj)

    resolve_context = None
    if context:
        resolve_context = ResolveContext(**context)
        validate_targets(game_state, resolve_context)

    cost_override, free_cast, alt_tag, alt_extra_costs = _resolve_alternative_cost(
        effect_graph, resolve_context
    )
    cost_text = None if free_cast else (cost_override or obj.mana_cost)
    cost = parse_mana_cost(cost_text, x_value=x_value)
    commander_tax = _commander_tax_preview(game_state, player_id, obj)
    if commander_tax:
        cost.generic += int(commander_tax)
    cost = apply_cast_cost_modifiers(game_state, player_id, obj, cost, resolve_context)
    game_state.prepared_casts[player_id] = {
        "object_id": obj.id,
        "x_value": x_value,
        "context": context or {},
        "cost": mana_cost_snapshot(cost),
        "alternative_cost": cost_override,
        "alternative_cost_tag": alt_tag,
        "free_cast": free_cast,
        "alternative_extra_costs": alt_extra_costs,
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
        attacker = game_state.objects.get(attacker_id)
        if attacker:
            game_state.event_bus.publish(Event(
                type="attacks",
                payload={
                    "object_id": attacker_id,
                    "controller_id": attacker.controller_id,
                    "owner_id": attacker.owner_id,
                    "cardTypes": list(attacker.types or []),
                },
            ))
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
    for attacker_id, blocker_ids in blockers.items():
        for blocker_id in blocker_ids:
            blocker = game_state.objects.get(blocker_id)
            attacker = game_state.objects.get(attacker_id)
            payload = {"object_id": blocker_id, "attacker_id": attacker_id}
            if blocker:
                payload.update({
                    "controller_id": blocker.controller_id,
                    "owner_id": blocker.owner_id,
                    "cardTypes": list(blocker.types or []),
                })
            if attacker:
                payload.update({
                    "attacker_controller_id": attacker.controller_id,
                    "attacker_owner_id": attacker.owner_id,
                    "attacker_cardTypes": list(attacker.types or []),
                })
            game_state.event_bus.publish(Event(type="blocks", payload=payload))
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

    graph = obj.effect_graphs[0] if obj.effect_graphs else None
    if not graph:
        raise ValueError("No effect graph available for mana ability.")

    steps = graph.get("steps") or []
    activated_steps = [
        step for step in steps
        if isinstance(step, dict)
        and isinstance(step.get("effect"), dict)
        and step.get("effect", {}).get("initiation") == "activated"
    ]
    mana_index = None
    for index, step in enumerate(activated_steps):
        tags = step.get("effect", {}).get("tags") or []
        resolution = step.get("effect", {}).get("resolution")
        if "mana" in tags and resolution == "immediate":
            mana_index = index
            break
    if mana_index is None:
        raise ValueError("No mana ability found in effect graph.")

    result = activate_ability(
        game_state,
        turn_manager,
        player_id,
        object_id,
        ability_index=mana_index,
        ability_type="activated",
        context=None,
    )
    if result.get("usesStack"):
        raise ValueError("Mana abilities must resolve immediately.")


def _find_effect_step_by_initiation(
    effect_graph: Dict[str, Any],
    initiation: str,
    effect_index: int,
) -> Optional[Dict[str, Any]]:
    steps = effect_graph.get("steps") or []
    matches = [
        step for step in steps
        if isinstance(step, dict)
        and isinstance(step.get("effect"), dict)
        and step.get("effect", {}).get("initiation") == initiation
    ]
    if effect_index < len(matches):
        return matches[effect_index]
    return None


def activate_ability(
    game_state,
    turn_manager,
    player_id: int,
    object_id: str,
    ability_index: int = 0,
    ability_type: str = "activated",
    context: Optional[dict] = None,
) -> Dict[str, Any]:
    """Activate an ability on a permanent.
    
    Args:
        game_state: The current game state
        turn_manager: The turn manager
        player_id: The player activating the ability
        object_id: The permanent with the ability
        ability_index: Index of the ability within the type (default: 0)
        ability_type: Type of ability ("activated", "triggered", etc.)
        context: Additional context (targets, choices, etc.)
    
    Returns:
        Dict with result status. If usesStack is false, returns resolved result.
    """
    require_priority(turn_manager, player_id)
    obj = game_state.objects.get(object_id)
    if not obj:
        raise ValueError("Permanent not found.")
    if obj.controller_id != player_id:
        raise ValueError("You do not control this permanent.")
    if not obj.effect_graphs:
        raise ValueError("Permanent has no abilities to activate.")

    graph = obj.effect_graphs[0]
    step = _find_effect_step_by_initiation(graph, ability_type, ability_index)
    if not step:
        raise ValueError(f"Invalid ability: {ability_type}-{ability_index}")

    effect = step.get("effect") or {}
    cost_spec = effect.get("cost") or {}
    _validate_ability_timing(game_state, turn_manager, player_id, obj, cost_spec.get("timing"))
    _check_activation_limit(obj, ability_index, cost_spec.get("limit"))
    resolve_context = None
    if context:
        resolve_context = ResolveContext(**context)
        if resolve_context.source_id is None:
            resolve_context.source_id = obj.id
        if resolve_context.controller_id is None:
            resolve_context.controller_id = player_id
        normalize_targets(game_state, resolve_context)
        validate_targets(game_state, resolve_context)
        enforce_ward_payment(game_state, resolve_context)
    validate_enter_choices_effect_graph(graph, context)
    validate_modal_choices_effect_graph(graph, context)
    costs = cost_spec.get("items") or []
    if costs:
        if any(cost.get("type") == "tap_self" for cost in costs):
            _require_tap_summoning_sickness_ok(game_state, obj)
            if obj.tapped:
                raise ValueError("Permanent is already tapped.")
        pay_activation_costs(
            game_state,
            player_id,
            obj,
            costs,
            resolve_context.choices if resolve_context else {},
        )
    _record_activation_use(obj, ability_index, cost_spec.get("limit"))

    # Resolve immediately if marked as immediate (mana abilities)
    uses_stack = effect.get("resolution") != "immediate"
    ability_id = effect.get("id") or f"{ability_type}-{ability_index}"
    
    if not uses_stack:
        # Resolve immediately without using the stack (mana abilities, etc.)
        game_state.log(f"[rules] resolving ability immediately (usesStack=false): {ability_id}")
        print(f"[graph] resolving ability immediately (usesStack=false): {ability_id}", flush=True)
        
        # Build resolve context if not already done
        if not resolve_context:
            resolve_context = ResolveContext(
                source_id=obj.id,
                controller_id=player_id,
            )
        
        resolver = EffectGraphResolver(game_state)
        result = resolver.resolve(graph, resolve_context, start_step_id=step.get("id"))
        turn_manager.after_mana_ability(player_id)
        return {"status": "resolved_immediately", "ability_id": ability_id, "result": result}

    # Normal case: push to stack
    stacked_context = context or {}
    stacked_context.setdefault("source_id", obj.id)
    stacked_context.setdefault("controller_id", player_id)
    game_state.stack.push(
        StackItem(
            kind="effect_graph",
            payload={
                "graph": graph,
                "start_step_id": step.get("id"),
                "context": stacked_context,
                "source_object_id": obj.id,
                "ability_id": ability_id,  # Include ability ID in payload
            },
            controller_id=player_id,
        )
    )
    _publish_becomes_target(game_state, obj.id, resolve_context)
    turn_manager.after_player_action(player_id)
    return {"status": "pushed_to_stack", "ability_id": ability_id}

