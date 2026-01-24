from __future__ import annotations

from typing import Dict, Optional, Tuple

from .continuous_helpers import (
    count_controlled,
    count_zone_cards,
    effect_sort_key,
    effects_of_type,
)
from .state import GameObject, GameState


def reset_characteristics(obj: GameObject) -> None:
    if obj.base_controller_id is not None:
        obj.controller_id = obj.base_controller_id
    if getattr(obj, "base_name", None) is not None:
        obj.name = obj.base_name
    if getattr(obj, "base_mana_cost", None) is not None:
        obj.mana_cost = obj.base_mana_cost
    if getattr(obj, "base_mana_value", None) is not None:
        obj.mana_value = obj.base_mana_value
    if getattr(obj, "base_type_line", None) is not None:
        obj.type_line = obj.base_type_line
    if getattr(obj, "base_oracle_text", None) is not None:
        obj.oracle_text = obj.base_oracle_text
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
    if getattr(obj, "base_effect_graphs", None):
        obj.effect_graphs = list(obj.base_effect_graphs)
    if getattr(obj, "base_etb_choices", None) is not None:
        obj.etb_choices = dict(obj.base_etb_choices)


def reset_layer_2_control(obj: GameObject) -> None:
    if obj.base_controller_id is not None:
        obj.controller_id = obj.base_controller_id


def reset_layer_3_text(obj: GameObject) -> None:
    if getattr(obj, "base_oracle_text", None) is not None:
        obj.oracle_text = obj.base_oracle_text


def reset_layer_4_type(obj: GameObject) -> None:
    if getattr(obj, "base_types", None):
        obj.types = list(obj.base_types)


def reset_layer_6_abilities(obj: GameObject) -> None:
    if obj.base_keywords is not None:
        obj.keywords = set(obj.base_keywords)


def reset_layer_7_pt(obj: GameObject) -> None:
    if obj.base_power is not None:
        obj.power = obj.base_power
    if obj.base_toughness is not None:
        obj.toughness = obj.base_toughness


def apply_layer_1_copy(game_state: GameState, obj: GameObject) -> None:
    copy_effects = list(effects_of_type(obj.temporary_effects, "copy_object"))
    if not copy_effects:
        return
    copy_effects = sorted(copy_effects, key=effect_sort_key)
    effect = copy_effects[-1]
    source_id = effect.get("source_id")
    if not source_id:
        return
    source = game_state.objects.get(source_id)
    if not source:
        return
    obj.name = source.name
    obj.mana_cost = source.mana_cost
    obj.mana_value = source.mana_value
    obj.type_line = source.type_line
    obj.oracle_text = source.oracle_text
    obj.types = list(source.types)
    obj.colors = list(source.colors)
    obj.power = source.power
    obj.toughness = source.toughness
    obj.keywords = set(source.keywords)
    obj.effect_graphs = list(source.effect_graphs)
    obj.etb_choices = dict(getattr(source, "etb_choices", {}) or {})


def copy_signature(obj: GameObject) -> Tuple:
    graphs = tuple(str(graph) for graph in (obj.effect_graphs or []))
    choices = tuple(str(item) for item in sorted((obj.etb_choices or {}).items()))
    return (
        obj.name,
        obj.mana_cost,
        obj.mana_value,
        tuple(obj.types),
        tuple(obj.colors),
        obj.power,
        obj.toughness,
        tuple(sorted(obj.keywords)),
        graphs,
        choices,
    )


def apply_layer_2_control(game_state: GameState, obj: GameObject) -> None:
    previous_controller = obj.controller_id
    for effect in effects_of_type(obj.temporary_effects, "set_controller"):
        controller_id = effect.get("controller_id")
        if controller_id is not None:
            obj.controller_id = controller_id
    if obj.controller_id == previous_controller:
        return
    prev_player = game_state.get_player(previous_controller)
    if obj.id in prev_player.battlefield:
        prev_player.battlefield.remove(obj.id)
    new_player = game_state.get_player(obj.controller_id)
    if obj.id not in new_player.battlefield:
        new_player.battlefield.append(obj.id)
    obj.is_attacking = False
    obj.is_blocking = False


def apply_layer_4_type(obj: GameObject) -> None:
    for effect in effects_of_type(obj.temporary_effects, "set_types"):
        types = effect.get("types")
        if isinstance(types, list):
            obj.types = list(types)
    for effect in effects_of_type(obj.temporary_effects, "add_type"):
        type_name = effect.get("type")
        if type_name and type_name not in obj.types:
            obj.types.append(type_name)
    for effect in effects_of_type(obj.temporary_effects, "remove_type"):
        type_name = effect.get("type")
        if type_name and type_name in obj.types:
            obj.types.remove(type_name)
    if "Creature" not in obj.types:
        obj.is_attacking = False
        obj.is_blocking = False


def apply_layer_3_text(obj: GameObject) -> None:
    for effect in effects_of_type(obj.temporary_effects, "set_oracle_text"):
        text = effect.get("text")
        if isinstance(text, str):
            obj.oracle_text = text
    for effect in effects_of_type(obj.temporary_effects, "append_oracle_text"):
        text = effect.get("text")
        if isinstance(text, str):
            base = obj.oracle_text or ""
            obj.oracle_text = f"{base}\n{text}".strip()
    for effect in effects_of_type(obj.temporary_effects, "remove_oracle_text"):
        text = effect.get("text")
        if isinstance(text, str) and obj.oracle_text:
            obj.oracle_text = obj.oracle_text.replace(text, "")

def apply_layer_5_color(obj: GameObject) -> None:
    for effect in effects_of_type(obj.temporary_effects, "set_colors"):
        colors = effect.get("colors")
        if isinstance(colors, list):
            obj.colors = list(colors)
    for effect in effects_of_type(obj.temporary_effects, "add_color"):
        color = effect.get("color")
        if color and color not in obj.colors:
            obj.colors.append(color)
    for effect in effects_of_type(obj.temporary_effects, "remove_color"):
        color = effect.get("color")
        if color and color in obj.colors:
            obj.colors.remove(color)


def derive_cda_value(game_state: GameState, obj: GameObject, effect: Dict) -> Optional[int]:
    source = effect.get("cda_source")
    if source == "controlled":
        type_name = effect.get("cda_type")
        if type_name in ("Permanent", "Any", None):
            type_name = None
        return count_controlled(game_state, obj.controller_id, type_name)
    if source == "zone":
        zone = effect.get("cda_zone")
        if zone in ("hand", "graveyard", "all_graveyards"):
            return count_zone_cards(game_state, obj.controller_id, zone)
    return None


def update_cda_values(game_state: GameState, obj: GameObject) -> None:
    cda_power = None
    cda_toughness = None
    for effect in effects_of_type(obj.temporary_effects, "set_cda_pt"):
        value = derive_cda_value(game_state, obj, effect)
        if value is None:
            continue
        target = effect.get("cda_set", "both")
        if target in ("both", "power"):
            cda_power = value
        if target in ("both", "toughness"):
            cda_toughness = value
    obj.cda_power = cda_power
    obj.cda_toughness = cda_toughness


def apply_layer_6_abilities(obj: GameObject) -> None:
    for effect in effects_of_type(obj.temporary_effects, "remove_keyword"):
        keyword = effect.get("keyword")
        if keyword and keyword in obj.keywords:
            obj.keywords.remove(keyword)
    for effect in effects_of_type(obj.temporary_effects, "add_keyword"):
        keyword = effect.get("keyword")
        if keyword:
            obj.keywords.add(keyword)


def apply_layer_7a_cda(obj: GameObject) -> None:
    if getattr(obj, "cda_power", None) is not None:
        obj.power = int(obj.cda_power)
    if getattr(obj, "cda_toughness", None) is not None:
        obj.toughness = int(obj.cda_toughness)


def apply_layer_7b_set_pt(obj: GameObject) -> None:
    for effect in effects_of_type(obj.temporary_effects, "set_power_toughness"):
        obj.power = int(effect.get("power", obj.power or 0))
        obj.toughness = int(effect.get("toughness", obj.toughness or 0))


def apply_layer_7c_modify_pt(obj: GameObject) -> None:
    for effect in effects_of_type(obj.temporary_effects, "modify_power_toughness"):
        obj.power = (obj.power or 0) + int(effect.get("power", 0))
        obj.toughness = (obj.toughness or 0) + int(effect.get("toughness", 0))


def apply_layer_7d_counters(obj: GameObject) -> None:
    counters: Dict[str, int] = obj.counters or {}
    if "+1/+1" in counters:
        obj.power = (obj.power or 0) + counters["+1/+1"]
        obj.toughness = (obj.toughness or 0) + counters["+1/+1"]
    if "-1/-1" in counters:
        obj.power = (obj.power or 0) - counters["-1/-1"]
        obj.toughness = (obj.toughness or 0) - counters["-1/-1"]

