from __future__ import annotations

from typing import Dict, List, Optional

from .choices_runtime import queue_choice
from .state import GameState


def _sort_key(effect: Dict) -> int:
    return int(effect.get("timestamp_order", 0))


def _consume_effect(effect: Dict, container: List[Dict]) -> None:
    uses = effect.get("uses")
    if uses is None:
        return
    remaining = int(uses) - 1
    if remaining <= 0:
        container.remove(effect)
    else:
        effect["uses"] = remaining


def _choose_effect(
    game_state: GameState,
    effects: List[Dict],
    event_key: str,
    player_id: Optional[int],
) -> Optional[Dict]:
    if not effects:
        return None
    if len(effects) == 1:
        return effects[0]
    choice_id = game_state.replacement_choices.get(event_key)
    if choice_id:
        for effect in effects:
            if effect.get("effect_id") == choice_id:
                return effect
    queue_choice(game_state, {
        "type": "replacement_effect",
        "key": event_key,
        "player_id": player_id,
        "options": [
            {"id": effect.get("effect_id"), "replacement_zone": effect.get("replacement_zone")}
            for effect in effects
        ],
    })
    game_state.log(f"Multiple replacements for {event_key}; defaulted to most recent.")
    return max(effects, key=_sort_key)


def resolve_replacement(
    game_state: GameState,
    effect_type: str,
    player_id: Optional[int],
    event_key: str,
    consume_choice: bool = True,
) -> Optional[Dict]:
    effects = [
        effect
        for effect in list(game_state.replacement_effects)
        if effect.get("type") == effect_type
        and (effect.get("player_id") is None or effect.get("player_id") == player_id)
    ]
    chosen = _choose_effect(game_state, effects, event_key, player_id)
    if not chosen:
        return None
    _consume_effect(chosen, game_state.replacement_effects)
    if consume_choice:
        game_state.replacement_choices.pop(event_key, None)
    return chosen


def apnap_player_order(game_state: GameState, player_ids: List[int]) -> List[int]:
    if not player_ids:
        return []
    active_index = getattr(getattr(game_state, "turn", None), "active_player_index", 0) or 0
    players = getattr(game_state, "players", []) or []
    ordered = []
    player_set = set(player_ids)
    for offset in range(len(players)):
        idx = (active_index + offset) % len(players)
        player = players[idx]
        if player.id in player_set:
            ordered.append(player.id)
    return ordered


def resolve_replacements_for_players(
    game_state: GameState,
    effect_type: str,
    player_ids: List[int],
    event_key_prefix: str,
) -> List[tuple[int, Optional[Dict]]]:
    ordered = apnap_player_order(game_state, player_ids)
    results: List[tuple[int, Optional[Dict]]] = []
    for player_id in ordered:
        event_key = f"{event_key_prefix}{player_id}"
        results.append((player_id, resolve_replacement(game_state, effect_type, player_id, event_key)))
    return results

