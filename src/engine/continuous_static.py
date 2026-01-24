from __future__ import annotations

from typing import Dict, List, Optional

from .conditions import evaluate_conditions
from .continuous_helpers import effect_sort_key, object_order
from .effects.active_effects import ActiveEffect
from .state import GameObject, GameState, ResolveContext
from .zones import ZONE_BATTLEFIELD


def stamp_static_effect(effect: Dict, source: GameObject, game_state: GameState) -> Dict:
    if "timestamp" not in effect:
        effect["timestamp"] = source.entered_turn or game_state.turn.turn_number
    if "timestamp_order" not in effect:
        effect["timestamp_order"] = object_order(source)
    return effect


def iter_applies_to(game_state: GameState, source: GameObject, applies_to: str) -> List[GameObject]:
    if applies_to == "self":
        return [source]
    if applies_to == "enchanted_creature":
        target = game_state.objects.get(source.attached_to) if source.attached_to else None
        return [target] if target and "Creature" in target.types else []
    if applies_to == "equipped_creature":
        target = game_state.objects.get(source.attached_to) if source.attached_to else None
        return [target] if target and "Creature" in target.types else []
    results: List[GameObject] = []
    for obj in game_state.objects.values():
        if obj.zone != ZONE_BATTLEFIELD or obj.phased_out:
            continue
        if applies_to == "creatures_you_control":
            if obj.controller_id == source.controller_id and "Creature" in obj.types:
                results.append(obj)
        elif applies_to == "all_creatures":
            if "Creature" in obj.types:
                results.append(obj)
        elif applies_to == "all_permanents":
            results.append(obj)
    return results


def build_static_effect(effect: Dict, source: GameObject, game_state: GameState) -> Optional[Dict]:
    effect_type = effect.get("type")
    if effect_type == "set_types":
        types = effect.get("types")
        if not isinstance(types, list):
            return None
        resolved_types = []
        for type_name in types:
            if type_name == "chosen_card_type":
                chosen = (source.etb_choices or {}).get("card_type")
                if not chosen:
                    return None
                resolved_types.append(chosen[:1].upper() + chosen[1:].lower())
            else:
                resolved_types.append(type_name)
        return stamp_static_effect({"type": "set_types", "types": resolved_types}, source, game_state)
    if effect_type == "add_type":
        type_name = effect.get("typeName")
        if type_name == "chosen_card_type":
            chosen = (source.etb_choices or {}).get("card_type")
            if not chosen:
                return None
            type_name = chosen[:1].upper() + chosen[1:].lower()
        return stamp_static_effect({"type": "add_type", "type": type_name}, source, game_state) if type_name else None
    if effect_type == "remove_type":
        type_name = effect.get("typeName")
        if type_name == "chosen_card_type":
            chosen = (source.etb_choices or {}).get("card_type")
            if not chosen:
                return None
            type_name = chosen[:1].upper() + chosen[1:].lower()
        return stamp_static_effect({"type": "remove_type", "type": type_name}, source, game_state) if type_name else None
    if effect_type == "set_colors":
        colors = effect.get("colors")
        if not isinstance(colors, list):
            return None
        resolved_colors = []
        for color in colors:
            if color == "chosen_color":
                chosen = (source.etb_choices or {}).get("color")
                if not chosen:
                    return None
                resolved_colors.append(chosen)
            else:
                resolved_colors.append(color)
        return stamp_static_effect({"type": "set_colors", "colors": resolved_colors}, source, game_state)
    if effect_type == "add_color":
        color = effect.get("color")
        if color == "chosen_color":
            chosen = (source.etb_choices or {}).get("color")
            if not chosen:
                return None
            color = chosen
        return stamp_static_effect({"type": "add_color", "color": color}, source, game_state) if color else None
    if effect_type == "remove_color":
        color = effect.get("color")
        if color == "chosen_color":
            chosen = (source.etb_choices or {}).get("color")
            if not chosen:
                return None
            color = chosen
        return stamp_static_effect({"type": "remove_color", "color": color}, source, game_state) if color else None
    if effect_type == "gain_keyword":
        keyword = effect.get("keyword")
        return stamp_static_effect({"type": "add_keyword", "keyword": keyword}, source, game_state) if keyword else None
    if effect_type == "change_power_toughness":
        return stamp_static_effect({
            "type": "modify_power_toughness",
            "power": int(effect.get("powerChange", 0)),
            "toughness": int(effect.get("toughnessChange", 0)),
        }, source, game_state)
    if effect_type == "change_control":
        return stamp_static_effect({"type": "set_controller", "controller_id": source.controller_id}, source, game_state)
    if effect_type == "cda_power_toughness":
        return stamp_static_effect({
            "type": "set_cda_pt",
            "cda_source": effect.get("cdaSource"),
            "cda_type": effect.get("cdaType"),
            "cda_zone": effect.get("cdaZone"),
            "cda_set": effect.get("cdaSet", "both"),
        }, source, game_state)
    return None


def gather_static_layer_effects(game_state: GameState, effect_types: Optional[set[str]] = None) -> Dict[str, List[Dict]]:
    by_object: Dict[str, List[Dict]] = {}
    registry_effects = _iter_registry_static_effects(game_state, effect_types)
    for obj_id, effects in registry_effects.items():
        by_object.setdefault(obj_id, []).extend(effects)
    for effects in by_object.values():
        effects.sort(key=effect_sort_key)
    return by_object


def _iter_registry_static_effects(
    game_state: GameState,
    effect_types: Optional[set[str]],
) -> Dict[str, List[Dict]]:
    by_object: Dict[str, List[Dict]] = {}
    for active in list(game_state.active_effect_registry.effects):
        if not _is_continuous_active(active, game_state):
            continue
        payload = _build_registry_payload(active)
        if not payload:
            continue
        payload_type = payload.get("type")
        if effect_types is not None and payload_type not in effect_types:
            continue
        source = game_state.objects.get(active.source_id)
        if not source:
            continue
        applies_to = _resolve_applies_to(active)
        for target in iter_applies_to(game_state, source, applies_to):
            if target.zone != ZONE_BATTLEFIELD or target.phased_out:
                continue
            context = ResolveContext(
                source_id=source.id,
                controller_id=source.controller_id,
                targets={"target": target.id},
            )
            conditions = [_to_dict(c) for c in active.effect_data.conditions]
            if conditions and not evaluate_conditions(game_state, conditions, context):
                continue
            effect = build_static_effect(payload, source, game_state)
            if not effect:
                continue
            message = (
                f"[graph] static_effect source={source.id} "
                f"target={target.id} effect={payload.get('type')}"
            )
            game_state.log(message)
            print(message, flush=True)
            by_object.setdefault(target.id, []).append(effect)
    for effects in by_object.values():
        effects.sort(key=effect_sort_key)
    return by_object


def _is_continuous_active(active: ActiveEffect, game_state: GameState) -> bool:
    body = active.effect_data.effect
    if getattr(body, "kind", None) != "continuous":
        return False
    duration = getattr(body, "duration", None)
    duration_type = getattr(duration, "type", None) if duration else None
    if duration_type != "while_in_zone":
        return False
    source = game_state.objects.get(active.source_id)
    if not source:
        return False
    zone = getattr(duration, "zone", None)
    if zone and source.zone != zone:
        return False
    return source.zone == ZONE_BATTLEFIELD and not source.phased_out


def _build_registry_payload(active: ActiveEffect) -> Optional[Dict]:
    body = active.effect_data.effect
    modifier = getattr(body, "modifier", None)
    if not modifier:
        return None
    if hasattr(modifier, "model_dump"):
        payload = modifier.model_dump(by_alias=True)
    else:
        payload = dict(modifier)
    payload_type = payload.get("type")
    if payload_type:
        payload["type"] = payload_type
    return payload


def _resolve_applies_to(active: ActiveEffect) -> str:
    body = active.effect_data.effect
    applies = getattr(body, "appliesTo", None)
    if isinstance(applies, dict):
        return applies.get("type") or "self"
    if isinstance(applies, str):
        return applies
    return "self"


def _to_dict(value) -> Dict:
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True)
    if isinstance(value, dict):
        return dict(value)
    return {}

