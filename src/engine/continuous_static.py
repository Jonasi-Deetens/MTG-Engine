from __future__ import annotations

from typing import Dict, List, Optional

from .ability_graph import AbilityGraphRuntimeAdapter
from .conditions import evaluate_conditions
from .continuous_helpers import effect_sort_key, object_order
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
    adapter = AbilityGraphRuntimeAdapter(game_state)
    by_object: Dict[str, List[Dict]] = {}
    for source in game_state.objects.values():
        if source.zone != ZONE_BATTLEFIELD or source.phased_out:
            continue
        if not source.ability_graphs:
            continue
        for graph in source.ability_graphs:
            if graph.get("abilityType") != "static":
                continue
            runtime = adapter.build_runtime(graph)
            if runtime.trigger or runtime.costs:
                continue
            for effect_node in runtime.effects:
                if not isinstance(effect_node, dict):
                    continue
                applies_to = effect_node.get("appliesTo", "self")
                payload = effect_node.get("effect")
                if not isinstance(payload, dict):
                    continue
                payload_type = payload.get("type")
                if effect_types is not None and payload_type not in effect_types:
                    continue
                for target in iter_applies_to(game_state, source, applies_to):
                    if target.zone != ZONE_BATTLEFIELD or target.phased_out:
                        continue
                    context = ResolveContext(
                        source_id=source.id,
                        controller_id=source.controller_id,
                        targets={"target": target.id},
                    )
                    if not evaluate_conditions(game_state, runtime.conditions, context):
                        continue
                    effect = build_static_effect(payload, source, game_state)
                    if not effect:
                        continue
                    by_object.setdefault(target.id, []).append(effect)
    for effects in by_object.values():
        effects.sort(key=effect_sort_key)
    return by_object

