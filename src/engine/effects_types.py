from __future__ import annotations

from typing import Any, Dict, List

from .effects_helpers import resolve_enter_choice_value, resolve_target_objects, normalize_card_type


def handle_protection(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    protection_type = effect.get("protectionType", "any")
    if protection_type == "chosen_color":
        chosen = resolve_enter_choice_value(resolver.game_state, context, "color")
        if not chosen:
            return {"type": "protection", "status": "missing_choice"}
        protection_type = chosen
    duration = effect.get("duration")
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        obj.protections.add(protection_type)
        if duration and duration != "permanent":
            resolver._add_temporary_effect(obj, {
                "type": "add_protection",
                "protection": protection_type,
                "duration": duration,
            })
        results.append({"object_id": obj.id, "protection": protection_type})
    if not results:
        return {"type": "protection", "status": "no_target"}
    return {"type": "protection", "results": results}


def handle_gain_keyword(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    keyword = effect.get("keyword")
    if not keyword:
        return {"type": "gain_keyword", "status": "no_target"}
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {"type": "add_keyword", "keyword": keyword, "duration": effect.get("duration")})
        results.append({"object_id": obj.id, "keyword": keyword})
    if not results:
        return {"type": "gain_keyword", "status": "no_target"}
    return {"type": "gain_keyword", "results": results}


def handle_change_power_toughness(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_creature")):
        resolver._add_temporary_effect(obj, {
            "type": "modify_power_toughness",
            "power": int(effect.get("powerChange", 0)),
            "toughness": int(effect.get("toughnessChange", 0)),
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "change_power_toughness", "status": "no_target"}
    return {"type": "change_power_toughness", "results": results}


def handle_set_oracle_text(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    text = effect.get("text")
    if not isinstance(text, str):
        return {"type": "set_oracle_text", "status": "invalid_text"}
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "set_oracle_text",
            "text": text,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "set_oracle_text", "status": "no_target"}
    return {"type": "set_oracle_text", "results": results}


def handle_append_oracle_text(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    text = effect.get("text")
    if not isinstance(text, str):
        return {"type": "append_oracle_text", "status": "invalid_text"}
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "append_oracle_text",
            "text": text,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "append_oracle_text", "status": "no_target"}
    return {"type": "append_oracle_text", "results": results}


def handle_remove_oracle_text(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    text = effect.get("text")
    if not isinstance(text, str):
        return {"type": "remove_oracle_text", "status": "invalid_text"}
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "remove_oracle_text",
            "text": text,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "remove_oracle_text", "status": "no_target"}
    return {"type": "remove_oracle_text", "results": results}


def handle_set_types(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    types = effect.get("types")
    if not isinstance(types, list):
        return {"type": "set_types", "status": "invalid_types"}
    resolved_types = []
    for type_name in types:
        if type_name == "chosen_card_type":
            chosen = resolve_enter_choice_value(resolver.game_state, context, "card_type")
            if not chosen:
                return {"type": "set_types", "status": "missing_choice"}
            resolved_types.append(normalize_card_type(chosen))
        else:
            resolved_types.append(type_name)
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "set_types",
            "types": resolved_types,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id, "types": resolved_types})
    if not results:
        return {"type": "set_types", "status": "no_target"}
    return {"type": "set_types", "results": results}


def handle_add_type(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    type_name = effect.get("typeName")
    if not type_name:
        return {"type": "add_type", "status": "invalid_type"}
    if type_name == "chosen_card_type":
        chosen = resolve_enter_choice_value(resolver.game_state, context, "card_type")
        if not chosen:
            return {"type": "add_type", "status": "missing_choice"}
        type_name = normalize_card_type(chosen)
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "add_type",
            "type": type_name,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id, "type": type_name})
    if not results:
        return {"type": "add_type", "status": "no_target"}
    return {"type": "add_type", "results": results}


def handle_remove_type(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    type_name = effect.get("typeName")
    if not type_name:
        return {"type": "remove_type", "status": "invalid_type"}
    if type_name == "chosen_card_type":
        chosen = resolve_enter_choice_value(resolver.game_state, context, "card_type")
        if not chosen:
            return {"type": "remove_type", "status": "missing_choice"}
        type_name = normalize_card_type(chosen)
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "remove_type",
            "type": type_name,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id, "type": type_name})
    if not results:
        return {"type": "remove_type", "status": "no_target"}
    return {"type": "remove_type", "results": results}


def handle_set_colors(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    colors = effect.get("colors")
    if not isinstance(colors, list):
        return {"type": "set_colors", "status": "invalid_colors"}
    resolved_colors = []
    for color in colors:
        if color == "chosen_color":
            chosen = resolve_enter_choice_value(resolver.game_state, context, "color")
            if not chosen:
                return {"type": "set_colors", "status": "missing_choice"}
            resolved_colors.append(chosen)
        else:
            resolved_colors.append(color)
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "set_colors",
            "colors": resolved_colors,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id, "colors": resolved_colors})
    if not results:
        return {"type": "set_colors", "status": "no_target"}
    return {"type": "set_colors", "results": results}


def handle_add_color(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    color = effect.get("color")
    if not color:
        return {"type": "add_color", "status": "invalid_color"}
    if color == "chosen_color":
        chosen = resolve_enter_choice_value(resolver.game_state, context, "color")
        if not chosen:
            return {"type": "add_color", "status": "missing_choice"}
        color = chosen
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "add_color",
            "color": color,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "add_color", "status": "no_target"}
    return {"type": "add_color", "results": results}


def handle_remove_color(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    color = effect.get("color")
    if not color:
        return {"type": "remove_color", "status": "invalid_color"}
    if color == "chosen_color":
        chosen = resolve_enter_choice_value(resolver.game_state, context, "color")
        if not chosen:
            return {"type": "remove_color", "status": "missing_choice"}
        color = chosen
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "target_permanent")):
        resolver._add_temporary_effect(obj, {
            "type": "remove_color",
            "color": color,
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "remove_color", "status": "no_target"}
    return {"type": "remove_color", "results": results}


def handle_cda_power_toughness(resolver, effect: Dict[str, Any], context) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    for obj in resolve_target_objects(resolver.game_state, context, effect.get("target", "self")):
        resolver._add_temporary_effect(obj, {
            "type": "set_cda_pt",
            "cda_source": effect.get("cdaSource"),
            "cda_type": effect.get("cdaType"),
            "cda_zone": effect.get("cdaZone"),
            "cda_set": effect.get("cdaSet", "both"),
            "duration": effect.get("duration"),
        })
        results.append({"object_id": obj.id})
    if not results:
        return {"type": "cda_power_toughness", "status": "no_target"}
    return {"type": "cda_power_toughness", "results": results}

