from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from .ability_graph import AbilityGraphRuntimeAdapter
from .conditions import evaluate_conditions
from .state import GameState, ResolveContext, GameObject
from .zones import ZONE_BATTLEFIELD


def _effects_of_type(effects: Iterable[Dict], effect_type: str) -> Iterable[Dict]:
    return (effect for effect in effects if effect.get("type") == effect_type)


def _effect_sort_key(effect: Dict) -> Tuple[int, int]:
    return (
        int(effect.get("timestamp", 0)),
        int(effect.get("timestamp_order", 0)),
    )


def _object_order(obj: GameObject) -> int:
    try:
        return int(obj.id.split("_", 1)[1])
    except (IndexError, ValueError, AttributeError):
        return 0


def _stamp_static_effect(effect: Dict, source: GameObject, game_state: GameState) -> Dict:
    if "timestamp" not in effect:
        effect["timestamp"] = source.entered_turn or game_state.turn.turn_number
    if "timestamp_order" not in effect:
        effect["timestamp_order"] = _object_order(source)
    return effect


def _iter_applies_to(game_state: GameState, source: GameObject, applies_to: str) -> List[GameObject]:
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


def _build_static_effect(effect: Dict, source: GameObject, game_state: GameState) -> Optional[Dict]:
    effect_type = effect.get("type")
    if effect_type == "set_types":
        types = effect.get("types")
        return _stamp_static_effect({"type": "set_types", "types": types}, source, game_state) if isinstance(types, list) else None
    if effect_type == "add_type":
        type_name = effect.get("typeName")
        return _stamp_static_effect({"type": "add_type", "type": type_name}, source, game_state) if type_name else None
    if effect_type == "remove_type":
        type_name = effect.get("typeName")
        return _stamp_static_effect({"type": "remove_type", "type": type_name}, source, game_state) if type_name else None
    if effect_type == "set_colors":
        colors = effect.get("colors")
        return _stamp_static_effect({"type": "set_colors", "colors": colors}, source, game_state) if isinstance(colors, list) else None
    if effect_type == "add_color":
        color = effect.get("color")
        return _stamp_static_effect({"type": "add_color", "color": color}, source, game_state) if color else None
    if effect_type == "remove_color":
        color = effect.get("color")
        return _stamp_static_effect({"type": "remove_color", "color": color}, source, game_state) if color else None
    if effect_type == "gain_keyword":
        keyword = effect.get("keyword")
        return _stamp_static_effect({"type": "add_keyword", "keyword": keyword}, source, game_state) if keyword else None
    if effect_type == "change_power_toughness":
        return _stamp_static_effect({
            "type": "modify_power_toughness",
            "power": int(effect.get("powerChange", 0)),
            "toughness": int(effect.get("toughnessChange", 0)),
        }, source, game_state)
    if effect_type == "change_control":
        return _stamp_static_effect({"type": "set_controller", "controller_id": source.controller_id}, source, game_state)
    if effect_type == "cda_power_toughness":
        return _stamp_static_effect({
            "type": "set_cda_pt",
            "cda_source": effect.get("cdaSource"),
            "cda_type": effect.get("cdaType"),
            "cda_zone": effect.get("cdaZone"),
            "cda_set": effect.get("cdaSet", "both"),
        }, source, game_state)
    return None


def _gather_static_layer_effects(game_state: GameState, effect_types: Optional[set[str]] = None) -> Dict[str, List[Dict]]:
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
            if runtime.trigger or runtime.cost:
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
                for target in _iter_applies_to(game_state, source, applies_to):
                    if target.zone != ZONE_BATTLEFIELD or target.phased_out:
                        continue
                    context = ResolveContext(
                        source_id=source.id,
                        controller_id=source.controller_id,
                        targets={"target": target.id},
                    )
                    if not evaluate_conditions(game_state, runtime.conditions, context):
                        continue
                    effect = _build_static_effect(payload, source, game_state)
                    if not effect:
                        continue
                    by_object.setdefault(target.id, []).append(effect)
    return by_object


def _reset_characteristics(obj) -> None:
    if obj.base_controller_id is not None:
        obj.controller_id = obj.base_controller_id
    if obj.base_power is not None:
        obj.power = obj.base_power
    if obj.base_toughness is not None:
        obj.toughness = obj.base_toughness
    if obj.base_keywords is not None:
        obj.keywords = set(obj.base_keywords)
    if getattr(obj, "base_types", None):
        obj.types = list(obj.base_types)
    if getattr(obj, "base_colors", None):
        obj.colors = list(obj.base_colors)


def _reset_layer_2_control(obj) -> None:
    if obj.base_controller_id is not None:
        obj.controller_id = obj.base_controller_id


def _reset_layer_4_type(obj) -> None:
    if getattr(obj, "base_types", None):
        obj.types = list(obj.base_types)


def _reset_layer_6_abilities(obj) -> None:
    if obj.base_keywords is not None:
        obj.keywords = set(obj.base_keywords)


def _reset_layer_7_pt(obj) -> None:
    if obj.base_power is not None:
        obj.power = obj.base_power
    if obj.base_toughness is not None:
        obj.toughness = obj.base_toughness


def _controller_signature(obj: GameObject) -> Tuple[str, int]:
    return (obj.id, obj.controller_id)


def _type_signature(obj: GameObject) -> Tuple[str, Tuple[str, ...]]:
    return (obj.id, tuple(obj.types))


def _keyword_signature(obj: GameObject) -> Tuple[str, Tuple[str, ...]]:
    return (obj.id, tuple(sorted(obj.keywords)))


def _pt_signature(obj: GameObject) -> Tuple[str, int, int]:
    return (obj.id, int(obj.power or 0), int(obj.toughness or 0))


def _count_controlled(game_state: GameState, controller_id: int, type_name: Optional[str]) -> int:
    count = 0
    for obj in game_state.objects.values():
        if obj.zone != ZONE_BATTLEFIELD or obj.phased_out:
            continue
        if obj.controller_id != controller_id:
            continue
        if type_name and type_name not in obj.types:
            continue
        count += 1
    return count


def _count_zone_cards(game_state: GameState, controller_id: int, zone: str) -> int:
    if zone == "all_graveyards":
        return sum(len(player.graveyard) for player in game_state.players)
    player = game_state.get_player(controller_id)
    if zone == "hand":
        return len(player.hand)
    if zone == "graveyard":
        return len(player.graveyard)
    return 0


def _derive_cda_value(game_state: GameState, obj: GameObject, effect: Dict) -> Optional[int]:
    source = effect.get("cda_source")
    if source == "controlled":
        type_name = effect.get("cda_type")
        if type_name in ("Permanent", "Any", None):
            type_name = None
        return _count_controlled(game_state, obj.controller_id, type_name)
    if source == "zone":
        zone = effect.get("cda_zone")
        if zone in ("hand", "graveyard", "all_graveyards"):
            return _count_zone_cards(game_state, obj.controller_id, zone)
    return None


def _update_cda_values(game_state: GameState, obj: GameObject) -> None:
    cda_power = None
    cda_toughness = None
    for effect in _effects_of_type(obj.temporary_effects, "set_cda_pt"):
        value = _derive_cda_value(game_state, obj, effect)
        if value is None:
            continue
        target = effect.get("cda_set", "both")
        if target in ("both", "power"):
            cda_power = value
        if target in ("both", "toughness"):
            cda_toughness = value
    obj.cda_power = cda_power
    obj.cda_toughness = cda_toughness


def _apply_layer_6_abilities(obj) -> None:
    for effect in _effects_of_type(obj.temporary_effects, "remove_keyword"):
        keyword = effect.get("keyword")
        if keyword and keyword in obj.keywords:
            obj.keywords.remove(keyword)
    for effect in _effects_of_type(obj.temporary_effects, "add_keyword"):
        keyword = effect.get("keyword")
        if keyword:
            obj.keywords.add(keyword)


def _apply_layer_2_control(obj) -> None:
    for effect in _effects_of_type(obj.temporary_effects, "set_controller"):
        controller_id = effect.get("controller_id")
        if controller_id is not None:
            obj.controller_id = controller_id


def _apply_layer_4_type(obj) -> None:
    for effect in _effects_of_type(obj.temporary_effects, "set_types"):
        types = effect.get("types")
        if isinstance(types, list):
            obj.types = list(types)
    for effect in _effects_of_type(obj.temporary_effects, "add_type"):
        type_name = effect.get("type")
        if type_name and type_name not in obj.types:
            obj.types.append(type_name)
    for effect in _effects_of_type(obj.temporary_effects, "remove_type"):
        type_name = effect.get("type")
        if type_name and type_name in obj.types:
            obj.types.remove(type_name)


def _apply_layer_5_color(obj) -> None:
    for effect in _effects_of_type(obj.temporary_effects, "set_colors"):
        colors = effect.get("colors")
        if isinstance(colors, list):
            obj.colors = list(colors)
    for effect in _effects_of_type(obj.temporary_effects, "add_color"):
        color = effect.get("color")
        if color and color not in obj.colors:
            obj.colors.append(color)
    for effect in _effects_of_type(obj.temporary_effects, "remove_color"):
        color = effect.get("color")
        if color and color in obj.colors:
            obj.colors.remove(color)


def _apply_layer_7a_cda(obj) -> None:
    if getattr(obj, "cda_power", None) is not None:
        obj.power = int(obj.cda_power)
    if getattr(obj, "cda_toughness", None) is not None:
        obj.toughness = int(obj.cda_toughness)


def _apply_layer_7b_set_pt(obj) -> None:
    for effect in _effects_of_type(obj.temporary_effects, "set_power_toughness"):
        obj.power = int(effect.get("power", obj.power or 0))
        obj.toughness = int(effect.get("toughness", obj.toughness or 0))


def _apply_layer_7c_modify_pt(obj) -> None:
    for effect in _effects_of_type(obj.temporary_effects, "modify_power_toughness"):
        obj.power = (obj.power or 0) + int(effect.get("power", 0))
        obj.toughness = (obj.toughness or 0) + int(effect.get("toughness", 0))


def _apply_layer_7d_counters(obj) -> None:
    counters: Dict[str, int] = obj.counters or {}
    if "+1/+1" in counters:
        obj.power = (obj.power or 0) + counters["+1/+1"]
        obj.toughness = (obj.toughness or 0) + counters["+1/+1"]
    if "-1/-1" in counters:
        obj.power = (obj.power or 0) - counters["-1/-1"]
        obj.toughness = (obj.toughness or 0) - counters["-1/-1"]


def apply_continuous_effects(game_state: GameState) -> None:
    battlefield = [
        obj for obj in game_state.objects.values()
        if obj.zone == ZONE_BATTLEFIELD and not obj.phased_out
    ]
    for obj in battlefield:
        _reset_characteristics(obj)

    def apply_layer(
        effect_types: Optional[set[str]],
        apply_fn,
        recompute_until_stable: bool = False,
        signature_fn=None,
        reset_fn=None,
        pre_apply_fn=None,
    ) -> None:
        previous_signature = None
        max_iterations = 5
        for _ in range(max_iterations):
            static_effects = _gather_static_layer_effects(game_state, effect_types)
            for obj in battlefield:
                base_effects = list(obj.temporary_effects)
                if obj.id in static_effects:
                    obj.temporary_effects = base_effects + static_effects[obj.id]
                else:
                    obj.temporary_effects = base_effects
                obj.temporary_effects = sorted(obj.temporary_effects, key=_effect_sort_key)
                if reset_fn:
                    reset_fn(obj)
                if pre_apply_fn:
                    pre_apply_fn(obj)
                apply_fn(obj)
                obj.temporary_effects = base_effects
            if not recompute_until_stable or not signature_fn:
                break
            signature = tuple(signature_fn(obj) for obj in battlefield)
            if signature == previous_signature:
                break
            previous_signature = signature

    apply_layer(
        {"change_control"},
        _apply_layer_2_control,
        recompute_until_stable=True,
        signature_fn=_controller_signature,
        reset_fn=_reset_layer_2_control,
    )
    apply_layer(
        {"set_types", "add_type", "remove_type"},
        _apply_layer_4_type,
        recompute_until_stable=True,
        signature_fn=_type_signature,
        reset_fn=_reset_layer_4_type,
    )
    apply_layer({"set_colors", "add_color", "remove_color"}, _apply_layer_5_color)
    apply_layer(
        {"gain_keyword"},
        _apply_layer_6_abilities,
        recompute_until_stable=True,
        signature_fn=_keyword_signature,
        reset_fn=_reset_layer_6_abilities,
    )
    apply_layer(
        {"cda_power_toughness"},
        _apply_layer_7a_cda,
        recompute_until_stable=True,
        signature_fn=_pt_signature,
        reset_fn=_reset_layer_7_pt,
        pre_apply_fn=lambda obj: _update_cda_values(game_state, obj),
    )
    apply_layer(
        set(),
        _apply_layer_7b_set_pt,
        recompute_until_stable=True,
        signature_fn=_pt_signature,
        reset_fn=_reset_layer_7_pt,
    )
    apply_layer(
        {"change_power_toughness"},
        _apply_layer_7c_modify_pt,
        recompute_until_stable=True,
        signature_fn=_pt_signature,
        reset_fn=_reset_layer_7_pt,
    )
    apply_layer(set(), _apply_layer_7d_counters)

