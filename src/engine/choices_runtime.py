from __future__ import annotations

from typing import Any, Dict, List


def _apnap_index(game_state, player_id: int) -> int:
    players = getattr(game_state, "players", []) or []
    if not players:
        return 0
    start = getattr(getattr(game_state, "turn", None), "active_player_index", 0) or 0
    order = []
    for offset in range(len(players)):
        idx = (start + offset) % len(players)
        order.append(players[idx].id)
    try:
        return order.index(player_id)
    except ValueError:
        return len(order)


def queue_choice(game_state, entry: Dict[str, Any]) -> None:
    if not isinstance(game_state.choices, dict):
        game_state.choices = {}
    pending = game_state.choices.get("pending")
    if not isinstance(pending, list):
        pending = []
    player_id = entry.get("player_id")
    if player_id is not None:
        entry["apnap_index"] = _apnap_index(game_state, int(player_id))
    pending.append(entry)
    if any(isinstance(item, dict) and "apnap_index" in item for item in pending):
        indexed = list(enumerate(pending))
        indexed.sort(key=lambda pair: (pair[1].get("apnap_index", 9999), pair[0]))
        pending = [item for _, item in indexed]
    game_state.choices["pending"] = pending

