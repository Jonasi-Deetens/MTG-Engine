from __future__ import annotations

from typing import Any, Dict, List

from .effects_helpers import (
    resolve_target_objects,
    resolve_target_object,
    resolve_effect_players,
    resolve_target_list_for_player,
    normalize_card_type,
)
from .state import ResolveContext
from .events import Event
from .targets import resolve_object_id, resolve_player_id
from .zones import ZONE_BATTLEFIELD, ZONE_EXILE, ZONE_GRAVEYARD, ZONE_HAND, ZONE_LIBRARY


def handle_untap(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("untapTarget", "self")):
        obj.tapped = False
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "untap", "status": "no_target"}
    return {"type": "untap", "results": results}


def handle_tap(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("untapTarget", "self")):
        obj.tapped = True
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "tap", "status": "no_target"}
    return {"type": "tap", "results": results}


def handle_destroy(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver.game_state.destroy_object(obj.id)
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "destroy", "status": "no_target"}
    return {"type": "destroy", "results": results}


def handle_exile(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver.game_state.move_object(obj.id, ZONE_EXILE)
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "exile", "status": "no_target"}
    return {"type": "exile", "results": results}


def handle_return(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver.game_state.move_object(obj.id, ZONE_HAND)
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "return", "status": "no_target"}
    return {"type": "return", "results": results}


def handle_sacrifice(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver.game_state.sacrifice_object(obj.id)
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "sacrifice", "status": "no_target"}
    return {"type": "sacrifice", "results": results}


def handle_search(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    """Handle search effect - find cards in a zone matching criteria.
    
    Search selections should be provided in context.targets_by_effect[node_id].search_results_by_player
    before resolution. The stack resolver checks for and requests these choices before calling resolve.
    """
    zone = effect.get("zone", ZONE_LIBRARY)
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "search", "status": "no_player"}
    merged_targets = dict(context.targets or {})
    targets_by_effect = getattr(context, "targets_by_effect", None)
    if isinstance(targets_by_effect, dict):
        node_id = effect.get("_node_id")
        override = targets_by_effect.get(node_id) if node_id else None
        if isinstance(override, dict):
            merged_targets.update(override)
    results = []
    reveal_found = bool(effect.get("revealFound"))
    destination_zone = effect.get("putFoundTo")
    shuffle_after = bool(effect.get("shuffleAfter"))
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        pool = getattr(player, zone, [])
        filtered_pool = _filter_search_pool(resolver, effect, context, player_id, pool)
        temp_context = ResolveContext(targets=merged_targets)
        found_ids = resolve_target_list_for_player(temp_context, "search_results", player_id)
        
        message = (
            f"[graph] search player={player_id} pool={len(pool)} "
            f"filtered={len(filtered_pool)} found={found_ids}"
        )
        resolver.game_state.log(message)
        print(message, flush=True)
        
        # Filter found_ids against filtered_pool, but fall back to pool check when
        # filtered_pool is empty (e.g. no GameObjects exist, only IDs)
        if filtered_pool:
            valid_found = [obj_id for obj_id in found_ids if obj_id in filtered_pool]
        else:
            valid_found = [obj_id for obj_id in found_ids if obj_id in pool]
        moved = []
        if destination_zone and valid_found:
            dest_zone = destination_zone
            for obj_id in valid_found:
                resolver.game_state.move_object(obj_id, dest_zone)
                moved.append(obj_id)
        if shuffle_after:
            resolver.game_state.zone_manager.shuffle_library(player_id)
        if reveal_found and valid_found:
            resolver.game_state.log(f"[graph] reveal_found player={player_id} cards={valid_found}")
        results.append({
            "player_id": player_id,
            "zone": zone,
            "found": valid_found,
            "filtered_pool": filtered_pool,  # Include for frontend reference
            "moved": moved,
            "revealed": reveal_found,
            "shuffled": shuffle_after,
        })
    return {"type": "search", "results": results} if len(results) > 1 else {"type": "search", **results[0]}


def _get_search_selection_for_node(context, node_id: str, player_id: int) -> List[str]:
    if not node_id or not isinstance(getattr(context, "targets_by_effect", None), dict):
        return []
    node_targets = context.targets_by_effect.get(node_id, {})
    results_by_player = node_targets.get("search_results_by_player", {})
    selection = results_by_player.get(str(player_id)) or results_by_player.get(player_id)
    if isinstance(selection, list):
        return selection
    if isinstance(selection, str):
        return [selection]
    return []


def _matches_card_type_or_subtype(obj, card_type: str) -> bool:
    """Check if object matches the card type (including subtypes like Aura, Equipment)."""
    if not card_type:
        return True
    # Check types list
    if card_type in (obj.types or []):
        return True
    # Check type_line for subtypes (e.g., "Enchantment — Aura" contains "Aura")
    if obj.type_line:
        type_line_lower = obj.type_line.lower()
        card_type_lower = card_type.lower()
        # Parse type_line for all words including subtypes
        for part in type_line_lower.replace("—", "-").replace("–", "-").split("-"):
            for word in part.strip().split():
                if word == card_type_lower:
                    return True
    return False


def _filter_search_pool(
    resolver_or_game_state,
    effect: Dict[str, Any],
    context,
    player_id: int,
    pool: List[str],
) -> List[str]:
    """Filter search pool based on effect criteria.
    
    Args:
        resolver_or_game_state: Either an EffectResolver (with .game_state) or GameState directly
        effect: The search effect configuration
        context: ResolveContext with triggering info
        player_id: The searching player's ID
        pool: List of object IDs to search through
    """
    if not pool:
        return []
    
    # Support both resolver.game_state and game_state directly
    game_state = getattr(resolver_or_game_state, 'game_state', None) or getattr(resolver_or_game_state, '_gs', None) or resolver_or_game_state
    
    card_type = effect.get("cardType")
    if isinstance(card_type, str) and card_type.lower() == "any":
        card_type = None
    is_basic_land = False
    if isinstance(card_type, str) and card_type.lower() in ("basic_land", "basic land"):
        is_basic_land = True
        card_type = None
    if isinstance(card_type, str):
        card_type = normalize_card_type(card_type)

    compare_op = effect.get("manaValueComparison")
    compare_source = effect.get("manaValueComparisonSource")
    compare_value = effect.get("manaValueComparisonValue")
    if compare_source and compare_source != "fixed_value":
        source_id = None
        if compare_source == "triggering_source":
            source_id = context.triggering_source_id
        elif compare_source == "triggering_aura":
            source_id = context.triggering_aura_id or context.triggering_source_id
        elif compare_source == "triggering_spell":
            source_id = context.triggering_spell_id or context.triggering_source_id
        source_obj = game_state.objects.get(source_id) if source_id else None
        compare_value = source_obj.mana_value if source_obj else None
    compare_value = compare_value if isinstance(compare_value, int) else None

    different_name = effect.get("differentName")
    different_config = {}
    if isinstance(different_name, dict) and different_name.get("enabled"):
        different_config = different_name
    elif different_name is True:
        different_config = {"enabled": True}

    compare_against_type = different_config.get("compareAgainstType")
    if compare_against_type and compare_against_type != "any":
        compare_against_type = normalize_card_type(compare_against_type)
    else:
        compare_against_type = None
    compare_against_zone = different_config.get("compareAgainstZone", "controlled")
    compare_against_source = different_config.get("compareAgainstSource")

    compare_names: set[str] = set()
    if different_config:
        compare_candidates: List[str] = []
        player = game_state.get_player(player_id)
        if compare_against_source:
            source_id = None
            if compare_against_source == "triggering_source":
                source_id = context.triggering_source_id
            elif compare_against_source == "triggering_aura":
                source_id = context.triggering_aura_id or context.triggering_source_id
            elif compare_against_source == "triggering_spell":
                source_id = context.triggering_spell_id or context.triggering_source_id
            elif compare_against_source == "source":
                source_id = context.source_id
            elif compare_against_source == "target":
                source_id = resolve_object_id(context, "target", None)
            if source_id:
                compare_candidates = [source_id]
        if not compare_candidates:
            if compare_against_zone == "controlled":
                compare_candidates = [
                    obj.id
                    for obj in game_state.objects.values()
                    if obj.zone == ZONE_BATTLEFIELD and obj.controller_id == player_id
                ]
            elif compare_against_zone == "battlefield":
                compare_candidates = [
                    obj.id
                    for obj in game_state.objects.values()
                    if obj.zone == ZONE_BATTLEFIELD
                ]
            elif compare_against_zone in ("graveyard", "hand", "library", "exile"):
                compare_candidates = list(getattr(player, compare_against_zone, []))
        for obj_id in compare_candidates:
            obj = game_state.objects.get(obj_id)
            if not obj:
                continue
            if compare_against_type and not _matches_card_type_or_subtype(obj, compare_against_type):
                continue
            if obj.name:
                compare_names.add(obj.name)

    def _compare(value: Optional[int]) -> bool:
        if compare_value is None or compare_op is None:
            return True
        if value is None:
            return False
        if compare_op == "<=":
            return value <= compare_value
        if compare_op == "<":
            return value < compare_value
        if compare_op == ">=":
            return value >= compare_value
        if compare_op == ">":
            return value > compare_value
        if compare_op == "==":
            return value == compare_value
        return True

    filtered: List[str] = []
    for obj_id in pool:
        obj = game_state.objects.get(obj_id)
        if not obj:
            continue
        if is_basic_land:
            if not (
                _matches_card_type_or_subtype(obj, "basic")
                and _matches_card_type_or_subtype(obj, "land")
            ):
                continue
        elif card_type and not _matches_card_type_or_subtype(obj, card_type):
            continue
        if not _compare(obj.mana_value):
            continue
        if compare_names and obj.name in compare_names:
            continue
        filtered.append(obj_id)
    return filtered


def handle_put_onto_battlefield(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    from .effects_internal.target_resolver import (
        should_infer_targets_from_effect,
        get_inferred_targets_from_previous_result,
    )
    
    from_effect = effect.get("fromEffect")
    card_ids = []
    
    # When fromEffect is specified, infer targets from previous effect's result
    # This allows omitting minTargets/maxTargets when using effect chaining
    if from_effect is not None and from_effect < len(context.previous_results):
        card_ids = get_inferred_targets_from_previous_result(
            context.previous_results, from_effect
        )
        if not card_ids:
            # Fallback to "found" key for backward compatibility
            card_ids = context.previous_results[from_effect].get("found", [])
    else:
        target_id = resolve_object_id(context, "target", None)
        if target_id:
            card_ids = [target_id]
    for obj_id in card_ids:
        obj = resolver.game_state.objects.get(obj_id)
        if obj:
            enter_copy_of = context.choices.get("enter_copy_of")
            if enter_copy_of:
                source = resolver.game_state.objects.get(enter_copy_of)
                if source:
                    resolver.game_state.object_manager.apply_enter_copy(obj, source)
            enter_choices = context.choices.get("enter_choices")
            if isinstance(enter_choices, dict):
                resolver.game_state.object_manager.apply_enter_choices(obj, enter_choices)
        resolver.game_state.move_object(obj_id, ZONE_BATTLEFIELD)
    message = f"[graph] put_onto_battlefield cards={card_ids}"
    resolver.game_state.log(message)
    print(message, flush=True)
    return {"type": "put_onto_battlefield", "cards": card_ids}


def handle_put_on_bottom_of_library(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    from .effects_internal.target_resolver import get_inferred_targets_from_previous_result

    from_effect = effect.get("fromEffect")
    card_ids: List[str] = []

    if from_effect is not None and from_effect < len(context.previous_results):
        card_ids = get_inferred_targets_from_previous_result(context.previous_results, from_effect)
        if not card_ids:
            card_ids = context.previous_results[from_effect].get("found", [])
    else:
        target_id = resolve_object_id(context, "target", None)
        if target_id:
            card_ids = [target_id]

    moved: List[str] = []
    for obj_id in card_ids:
        obj = resolver.game_state.objects.get(obj_id)
        if not obj:
            continue
        resolver.game_state.move_object(obj_id, ZONE_LIBRARY)
        moved.append(obj_id)

    message = f"[graph] put_on_bottom_of_library cards={moved}"
    resolver.game_state.log(message)
    print(message, flush=True)
    return {"type": "put_on_bottom_of_library", "cards": moved, "moved": moved}


def handle_look_at_pick_and_bottom(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = int(effect.get("amount", 1))
    pick_types = effect.get("pickTypes") or []
    if isinstance(pick_types, str):
        pick_types = [pick_types]
    pick_max = int(effect.get("pickMax", 1))
    pick_destination = effect.get("pickDestination", "hand")
    reveal_chosen = effect.get("revealChosen", True)
    order_bottom = effect.get("orderBottom", True)

    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "look_at_pick_and_bottom", "status": "no_player"}

    results: List[Dict[str, Any]] = []
    node_id = effect.get("_node_id")
    pick_node_id = f"{node_id}:pick" if node_id else None
    order_node_id = f"{node_id}:order" if node_id else None

    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        top_ids = list(player.library[:amount])
        if not top_ids:
            results.append({"player_id": player_id, "looked": []})
            continue

        def matches_types(obj_id: str) -> bool:
            if not pick_types:
                return True
            obj = resolver.game_state.objects.get(obj_id)
            if not obj:
                return False
            return any(_matches_card_type_or_subtype(obj, normalize_card_type(t)) for t in pick_types if t)

        pick_candidates = [obj_id for obj_id in top_ids if matches_types(obj_id)]
        picked_ids = _get_search_selection_for_node(context, pick_node_id or "", player_id)
        picked_id = next((obj_id for obj_id in picked_ids if obj_id in pick_candidates), None)
        if pick_max <= 0:
            picked_id = None

        if picked_id:
            destination = {
                "hand": ZONE_HAND,
                "battlefield": ZONE_BATTLEFIELD,
                "graveyard": ZONE_GRAVEYARD,
                "exile": ZONE_EXILE,
            }.get(pick_destination, ZONE_HAND)
            resolver.game_state.move_object(picked_id, destination)

        rest_ids = [obj_id for obj_id in top_ids if obj_id != picked_id]
        bottom_order = rest_ids
        if order_bottom and order_node_id:
            ordered = _get_search_selection_for_node(context, order_node_id, player_id)
            if ordered:
                ordered_filtered = [obj_id for obj_id in ordered if obj_id in rest_ids]
                remaining = [obj_id for obj_id in rest_ids if obj_id not in ordered_filtered]
                bottom_order = ordered_filtered + remaining

        if rest_ids:
            player.library = [obj_id for obj_id in player.library if obj_id not in rest_ids]
            player.library.extend(bottom_order)

        results.append({
            "player_id": player_id,
            "looked": top_ids,
            "picked": picked_id,
            "bottom": bottom_order,
            "revealed": bool(picked_id and reveal_chosen),
        })

    return {"type": "look_at_pick_and_bottom", "results": results} if len(results) > 1 else {"type": "look_at_pick_and_bottom", **results[0]}


def handle_attach(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    merged_targets = dict(context.targets or {})
    targets_by_effect = getattr(context, "targets_by_effect", None)
    if isinstance(targets_by_effect, dict):
        node_id = effect.get("_node_id")
        override = targets_by_effect.get(node_id) if node_id else None
        if isinstance(override, dict):
            merged_targets.update(override)
    temp_context = ResolveContext(
        source_id=context.source_id,
        controller_id=context.controller_id,
        triggering_source_id=context.triggering_source_id,
        triggering_aura_id=context.triggering_aura_id,
        triggering_spell_id=context.triggering_spell_id,
        targets=merged_targets,
        targets_by_effect=context.targets_by_effect,
        required_targets_by_effect=context.required_targets_by_effect,
        distinct_targets_by_effect=context.distinct_targets_by_effect,
        min_targets_by_effect=context.min_targets_by_effect,
        choices=context.choices,
        previous_results=context.previous_results,
    )
    attach_to = resolve_object_id(temp_context, "attach_to", effect.get("attachTo"))
    if attach_to in ("self", "source"):
        attach_to = context.source_id
    elif attach_to == "triggering_source":
        attach_to = context.triggering_source_id or context.source_id
    elif attach_to == "triggering_spell":
        attach_to = context.triggering_spell_id or context.triggering_source_id
    elif attach_to == "triggering_aura":
        aura_id = context.triggering_aura_id or context.triggering_source_id
        aura_obj = resolver.game_state.objects.get(aura_id) if aura_id else None
        if aura_obj and aura_obj.attached_to:
            attach_to = aura_obj.attached_to
        else:
            attach_to = aura_id
    elif isinstance(attach_to, str) and attach_to.startswith("target_"):
        attach_to = resolve_object_id(temp_context, "target", attach_to)
    if not attach_to:
        attach_to = resolve_object_id(temp_context, "target", None)
    from .effects_internal.target_resolver import get_inferred_targets_from_previous_result
    
    from_effect = effect.get("fromEffect")
    card_ids = []
    
    # When fromEffect is specified, infer targets from previous effect's result
    # This allows omitting minTargets/maxTargets when using effect chaining
    if from_effect is not None and from_effect < len(context.previous_results):
        prev_result = context.previous_results[from_effect]
        print(f"[graph] attach from_effect={from_effect} prev_result={prev_result}", flush=True)
        # Use helper function to get targets from common result keys
        card_ids = get_inferred_targets_from_previous_result(
            context.previous_results, from_effect
        )
        # Fallback for backward compatibility
        if not card_ids:
            card_ids = prev_result.get("found", []) or prev_result.get("cards", [])
    elif effect.get("attachSource"):
        if temp_context.source_id:
            card_ids = [temp_context.source_id]
    else:
        target_id = resolve_object_id(temp_context, "target", None)
        if target_id:
            card_ids = [target_id]
    attached = resolver.game_state.objects.get(attach_to) if attach_to else None
    results: List[Dict[str, Any]] = []
    for obj_id in card_ids:
        obj = resolver.game_state.objects.get(obj_id)
        if not obj:
            continue
        if not attached or attached.zone != ZONE_BATTLEFIELD or attached.phased_out:
            obj.attached_to = None
            results.append({"object_id": obj.id, "status": "invalid_target"})
            continue
        if "Equipment" in obj.types and "Creature" not in attached.types:
            obj.attached_to = None
            results.append({"object_id": obj.id, "status": "invalid_target"})
            continue
        if resolver.game_state.attachment_manager._is_illegal_attachment(obj, attached):
            obj.attached_to = None
            results.append({"object_id": obj.id, "status": "illegal_attachment"})
            continue
        obj.attached_to = attach_to
        results.append({"object_id": obj.id, "status": "attached"})
    message = f"[graph] attach cards={card_ids} attach_to={attach_to} results={results}"
    resolver.game_state.log(message)
    print(message, flush=True)
    return {"type": "attach", "cards": card_ids, "attach_to": attach_to, "results": results}


def handle_shuffle(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "shuffle", "status": "no_player"}
    import random
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        random.shuffle(player.library)
        results.append({"player_id": player_id})
    return {"type": "shuffle", "results": results} if len(results) > 1 else {"type": "shuffle", **results[0]}


def handle_counter_spell(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target_spell = resolve_object_id(context, "target", None)
    if not target_spell:
        return {"type": "counter_spell", "status": "no_target"}
    target_item = None
    for item in reversed(resolver.game_state.stack.items):
        if item.kind != "spell":
            continue
        if item.payload.get("object_id") == target_spell or item.payload.get("copy_of") == target_spell:
            target_item = item
            break
    if not target_item:
        return {"type": "counter_spell", "status": "not_on_stack"}
    resolver.game_state.stack.items.remove(target_item)
    if target_item.payload.get("object_id"):
        obj = resolver.game_state.objects.get(target_item.payload.get("object_id"))
        if obj:
            resolver.game_state.move_object(obj.id, ZONE_GRAVEYARD)
            resolver.game_state.event_bus.publish(Event(
                type="spell_countered",
                payload={"object_id": obj.id, "controller_id": obj.controller_id},
            ))
    else:
        resolver.game_state.event_bus.publish(Event(
            type="spell_countered",
            payload={"copy_of": target_item.payload.get("copy_of"), "controller_id": context.controller_id},
        ))
    return {"type": "counter_spell", "target": target_spell}


def handle_regenerate(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    obj = resolve_target_object(resolver.game_state, context, effect.get("target", "target_creature"))
    if not obj:
        return {"type": "regenerate", "status": "no_target"}
    obj.regenerate_shield = True
    return {"type": "regenerate", "object_id": obj.id}


def handle_phase_out(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    obj = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not obj:
        return {"type": "phase_out", "status": "no_target"}
    obj.phased_out = True
    obj.tapped = False
    obj.is_attacking = False
    obj.is_blocking = False
    for attached in resolver.game_state.objects.values():
        if attached.attached_to == obj.id and attached.zone == ZONE_BATTLEFIELD:
            attached.phased_out = True
    return {"type": "phase_out", "object_id": obj.id}


def handle_transform(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    obj = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not obj:
        return {"type": "transform", "status": "no_target"}
    obj.transformed = not obj.transformed
    obj.tapped = False
    obj.is_attacking = False
    obj.is_blocking = False
    return {"type": "transform", "object_id": obj.id}


def handle_flicker(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    obj = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not obj:
        return {"type": "flicker", "status": "no_target"}
    owner_id = obj.owner_id
    owner = resolver.game_state.get_player(owner_id)
    resolver.game_state.move_object(obj.id, ZONE_EXILE)
    if obj.id in owner.exile:
        owner.exile.remove(obj.id)
    resolver.game_state.move_object(obj.id, ZONE_BATTLEFIELD)
    if effect.get("returnUnderOwner", True):
        obj.controller_id = owner_id
    return {"type": "flicker", "object_id": obj.id}


def handle_change_control(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    obj = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not obj:
        return {"type": "change_control", "status": "no_target"}
    new_controller = resolve_player_id(context, context.controller_id)
    if new_controller is None:
        return {"type": "change_control", "status": "no_player"}
    original_controller = obj.controller_id
    obj.controller_id = new_controller
    obj.is_attacking = False
    obj.is_blocking = False
    duration = effect.get("duration")
    if duration and duration != "permanent":
        resolver._add_temporary_effect(obj, {
            "type": "set_controller",
            "controller_id": new_controller,
            "original_controller": original_controller,
            "duration": duration,
        })
    return {"type": "change_control", "object_id": obj.id, "controller_id": new_controller}

