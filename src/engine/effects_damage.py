from __future__ import annotations

from typing import Any, Dict, List

from .damage import apply_damage_to_object, apply_damage_to_player
from .effects_helpers import (
    resolve_effect_amount,
    resolve_target_objects,
    resolve_target_players,
    resolve_target_object,
)
from .targets import resolve_object_id


def handle_damage(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = resolve_effect_amount(effect, context, 0)
    target_type = effect.get("target", "any")
    results: List[Dict[str, Any]] = []
    if target_type in ("player", "any"):
        for player_id in resolve_target_players(context, context.controller_id, resolver.game_state):
            if player_id is not None and context.source_id:
                source = resolver.game_state.objects.get(context.source_id)
                if source:
                    apply_damage_to_player(resolver.game_state, source, player_id, amount)
                    results.append({"player_id": player_id, "amount": amount})
    if target_type in (
        "any",
        "target",
        "target_permanent",
        "target_creature",
        "target_artifact",
        "target_enchantment",
        "target_planeswalker",
    ):
        for obj in resolve_target_objects(resolver.game_state, context, target_type):
            if context.source_id:
                source = resolver.game_state.objects.get(context.source_id)
                if source:
                    apply_damage_to_object(resolver.game_state, source, obj, amount)
                    results.append({"object_id": obj.id, "amount": amount})
    if not results:
        return {"type": "damage", "status": "no_target"}
    return {"type": "damage", "results": results}


def handle_prevent_damage(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    amount = resolve_effect_amount(effect, context, 1)
    obj = resolve_target_object(resolver.game_state, context, effect.get("target", "target_permanent"))
    if obj:
        resolver._add_temporary_effect(obj, {
            "prevent_damage": amount,
            "duration": "until_end_of_turn",
            "controller_id": context.controller_id,
            "effect_id": resolver.game_state.next_replacement_effect_id(),
        })
        return {"type": "prevent_damage", "object_id": obj.id, "amount": amount}
    player_id = resolve_target_players(context, context.controller_id, resolver.game_state)
    player_id = player_id[0] if player_id else None
    if player_id is None:
        return {"type": "prevent_damage", "status": "no_target"}
    resolver.game_state.replacement_effects.append({
        "type": "prevent_damage",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "timestamp_order": resolver.game_state.effect_timestamp_counter + 1,
        "player_id": player_id,
        "amount": amount,
    })
    resolver.game_state.effect_timestamp_counter += 1
    return {"type": "prevent_damage", "player_id": player_id, "amount": amount}


def handle_redirect_damage(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    source_id = resolve_object_id(context, "sourceTarget", None)
    redirect_id = resolve_object_id(context, "redirectTarget", None)
    redirect_player_id = resolve_target_players(context, None, resolver.game_state)[0] if not redirect_id else None
    amount = resolve_effect_amount(effect, context, 1)
    if not source_id or (not redirect_id and redirect_player_id is None):
        return {"type": "redirect_damage", "status": "no_target"}
    entry = {
        "type": "redirect_damage",
        "effect_id": resolver.game_state.next_replacement_effect_id(),
        "timestamp_order": resolver.game_state.effect_timestamp_counter + 1,
        "source": source_id,
        "amount": amount,
    }
    if redirect_id:
        entry["redirect"] = redirect_id
    else:
        entry["redirect_player_id"] = redirect_player_id
    resolver.game_state.replacement_effects.append(entry)
    resolver.game_state.effect_timestamp_counter += 1
    redirect_label = redirect_id if redirect_id else f"player:{redirect_player_id}"
    resolver.game_state.debug_log.append(
        f"Redirect {amount} damage from {source_id} to {redirect_label}"
    )
    return {"type": "redirect_damage", "source": source_id, "redirect": redirect_label, "amount": amount}

