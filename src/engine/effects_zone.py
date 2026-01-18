from __future__ import annotations

from typing import Any, Dict, List

from .effects_helpers import resolve_target_objects, resolve_target_object, resolve_effect_players, resolve_target_list_for_player
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
    zone = effect.get("zone", ZONE_LIBRARY)
    player_ids = resolve_effect_players(resolver.game_state, context, effect, context.controller_id)
    if not player_ids:
        return {"type": "search", "status": "no_player"}
    results = []
    for player_id in player_ids:
        player = resolver.game_state.get_player(player_id)
        pool = getattr(player, zone, [])
        found_ids = resolve_target_list_for_player(context, "search_results", player_id)
        results.append({"player_id": player_id, "zone": zone, "found": [obj_id for obj_id in found_ids if obj_id in pool]})
    return {"type": "search", "results": results} if len(results) > 1 else {"type": "search", **results[0]}


def handle_put_onto_battlefield(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    from_effect = effect.get("fromEffect")
    card_ids = []
    if from_effect is not None and from_effect < len(context.previous_results):
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
                resolver.game_state._apply_enter_copy(obj, enter_copy_of)
            enter_choices = context.choices.get("enter_choices")
            if isinstance(enter_choices, dict):
                resolver.game_state._apply_enter_choices(obj, enter_choices)
        resolver.game_state.move_object(obj_id, ZONE_BATTLEFIELD)
    return {"type": "put_onto_battlefield", "cards": card_ids}


def handle_attach(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    attach_to = resolve_object_id(context, "attach_to", effect.get("attachTo"))
    from_effect = effect.get("fromEffect")
    card_ids = []
    if from_effect is not None and from_effect < len(context.previous_results):
        card_ids = context.previous_results[from_effect].get("found", [])
    else:
        target_id = resolve_object_id(context, "target", None)
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
        if resolver.game_state._is_illegal_attachment(obj, attached):
            obj.attached_to = None
            results.append({"object_id": obj.id, "status": "illegal_attachment"})
            continue
        obj.attached_to = attach_to
        results.append({"object_id": obj.id, "status": "attached"})
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
    return {"type": "phase_out", "object_id": obj.id}


def handle_transform(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    obj = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not obj:
        return {"type": "transform", "status": "no_target"}
    obj.transformed = not obj.transformed
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
    if effect.get("returnUnderOwner"):
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
    duration = effect.get("duration")
    if duration and duration != "permanent":
        resolver._add_temporary_effect(obj, {
            "type": "set_controller",
            "controller_id": new_controller,
            "original_controller": original_controller,
            "duration": duration,
        })
    return {"type": "change_control", "object_id": obj.id, "controller_id": new_controller}

