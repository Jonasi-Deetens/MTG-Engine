from __future__ import annotations

from typing import Any, Dict

from .effects_helpers import resolve_target_object
from .targets import resolve_player_id


def handle_replace_zone_change(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not target:
        return {"type": "replace_zone_change", "status": "no_target"}
    replacement_zone = effect.get("replacementZone")
    if not replacement_zone:
        return {"type": "replace_zone_change", "status": "invalid_replacement"}
    entry = {
        "type": "replace_zone_change",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "from_zone": effect.get("fromZone"),
        "to_zone": effect.get("toZone"),
        "replacement_zone": replacement_zone,
        "duration": effect.get("duration"),
        "controller_id": context.controller_id,
        "object_id": target.id,
    }
    uses = effect.get("uses")
    if uses is not None:
        entry["uses"] = int(uses)
    resolver._add_temporary_effect(target, entry)
    return {
        "type": "replace_zone_change",
        "object_id": target.id,
        "replacement_zone": replacement_zone,
    }


def handle_replace_destroy(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not target:
        return {"type": "replace_destroy", "status": "no_target"}
    replacement_zone = effect.get("replacementZone")
    if not replacement_zone:
        return {"type": "replace_destroy", "status": "invalid_replacement"}
    entry = {
        "type": "replace_destroy",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "replacement_zone": replacement_zone,
        "duration": effect.get("duration"),
        "controller_id": context.controller_id,
        "object_id": target.id,
    }
    uses = effect.get("uses")
    if uses is not None:
        entry["uses"] = int(uses)
    resolver._add_temporary_effect(target, entry)
    return {"type": "replace_destroy", "object_id": target.id, "replacement_zone": replacement_zone}


def handle_replace_sacrifice(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    target = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if not target:
        return {"type": "replace_sacrifice", "status": "no_target"}
    replacement_zone = effect.get("replacementZone")
    if not replacement_zone:
        return {"type": "replace_sacrifice", "status": "invalid_replacement"}
    entry = {
        "type": "replace_sacrifice",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "replacement_zone": replacement_zone,
        "duration": effect.get("duration"),
        "controller_id": context.controller_id,
        "object_id": target.id,
    }
    uses = effect.get("uses")
    if uses is not None:
        entry["uses"] = int(uses)
    resolver._add_temporary_effect(target, entry)
    return {"type": "replace_sacrifice", "object_id": target.id, "replacement_zone": replacement_zone}


def handle_replace_draw(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    player_id = resolve_player_id(context, context.controller_id)
    if player_id is None:
        return {"type": "replace_draw", "status": "no_player"}
    entry = {
        "type": "replace_draw",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "timestamp_order": resolver.game_state.effect_timestamp_counter + 1,
        "player_id": player_id,
        "replacement_zone": effect.get("replacementZone"),
    }
    uses = effect.get("uses")
    if uses is not None:
        entry["uses"] = int(uses)
    resolver.game_state.replacement_effects.append(entry)
    resolver.game_state.effect_timestamp_counter += 1
    return {"type": "replace_draw", "player_id": player_id, "replacement_zone": entry.get("replacement_zone")}


def handle_replace_discard(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    player_id = resolve_player_id(context, context.controller_id)
    if player_id is None:
        return {"type": "replace_discard", "status": "no_player"}
    entry = {
        "type": "replace_discard",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "timestamp_order": resolver.game_state.effect_timestamp_counter + 1,
        "player_id": player_id,
        "replacement_zone": effect.get("replacementZone"),
    }
    uses = effect.get("uses")
    if uses is not None:
        entry["uses"] = int(uses)
    resolver.game_state.replacement_effects.append(entry)
    resolver.game_state.effect_timestamp_counter += 1
    return {"type": "replace_discard", "player_id": player_id, "replacement_zone": entry.get("replacement_zone")}


def handle_replace_life_loss(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    player_id = resolve_player_id(context, context.controller_id)
    if player_id is None:
        return {"type": "replace_life_loss", "status": "no_player"}
    entry = {
        "type": "replace_life_loss",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "timestamp_order": resolver.game_state.effect_timestamp_counter + 1,
        "player_id": player_id,
        "replacement_amount": effect.get("replacementAmount"),
    }
    uses = effect.get("uses")
    if uses is not None:
        entry["uses"] = int(uses)
    resolver.game_state.replacement_effects.append(entry)
    resolver.game_state.effect_timestamp_counter += 1
    return {"type": "replace_life_loss", "player_id": player_id, "replacement_amount": entry.get("replacement_amount")}

