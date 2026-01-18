from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from .state import GameObject, GameState
from .zones import ZONE_BATTLEFIELD


def effects_of_type(effects: Iterable[Dict], effect_type: str) -> Iterable[Dict]:
    return (effect for effect in effects if effect.get("type") == effect_type)


def effect_sort_key(effect: Dict) -> Tuple[int, int]:
    return (
        int(effect.get("timestamp", 0)),
        int(effect.get("timestamp_order", 0)),
    )


def sort_effects_with_dependencies(effects: List[Dict]) -> List[Dict]:
    if not effects:
        return effects
    ordered = list(effects)
    keys: List[str] = []
    key_map: Dict[str, int] = {}
    for idx, effect in enumerate(ordered):
        key = (
            effect.get("effect_id")
            or effect.get("id")
            or effect.get("key")
            or f"idx:{idx}"
        )
        key = str(key)
        keys.append(key)
        key_map[key] = idx
    deps: Dict[str, set[str]] = {}
    for idx, effect in enumerate(ordered):
        raw = effect.get("depends_on") or effect.get("dependsOn") or effect.get("dependencies") or []
        dep_list = raw if isinstance(raw, list) else [raw]
        dep_keys = {str(dep) for dep in dep_list if str(dep) in key_map}
        deps[keys[idx]] = dep_keys
    indegree = {key: len(dep_set) for key, dep_set in deps.items()}
    adjacency: Dict[str, set[str]] = {key: set() for key in deps}
    for key, dep_set in deps.items():
        for dep in dep_set:
            adjacency[dep].add(key)
    base_order = sorted(keys, key=lambda k: effect_sort_key(ordered[key_map[k]]))
    queue = [key for key in base_order if indegree.get(key, 0) == 0]
    result: List[str] = []
    while queue:
        current = queue.pop(0)
        result.append(current)
        for neighbor in sorted(adjacency.get(current, []), key=lambda k: base_order.index(k)):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    if len(result) != len(keys):
        return sorted(ordered, key=effect_sort_key)
    return [ordered[key_map[key]] for key in result]


def object_order(obj: GameObject) -> int:
    try:
        return int(obj.id.split("_", 1)[1])
    except (IndexError, ValueError, AttributeError):
        return 0


def pt_baseline_snapshot(obj: GameObject) -> Tuple[Optional[int], Optional[int]]:
    return (obj.power, obj.toughness)


def pt_baseline_restore(obj: GameObject, snapshot: Tuple[Optional[int], Optional[int]]) -> None:
    obj.power, obj.toughness = snapshot


def controller_signature(obj: GameObject) -> Tuple[str, int]:
    return (obj.id, obj.controller_id)


def type_signature(obj: GameObject) -> Tuple[str, Tuple[str, ...]]:
    return (obj.id, tuple(obj.types))


def keyword_signature(obj: GameObject) -> Tuple[str, Tuple[str, ...]]:
    return (obj.id, tuple(sorted(obj.keywords)))


def pt_signature(obj: GameObject) -> Tuple[str, int, int]:
    return (obj.id, int(obj.power or 0), int(obj.toughness or 0))


def count_controlled(game_state: GameState, controller_id: int, type_name: Optional[str]) -> int:
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


def count_zone_cards(game_state: GameState, controller_id: int, zone: str) -> int:
    if zone == "all_graveyards":
        return sum(len(player.graveyard) for player in game_state.players)
    player = game_state.get_player(controller_id)
    if zone == "hand":
        return len(player.hand)
    if zone == "graveyard":
        return len(player.graveyard)
    return 0

