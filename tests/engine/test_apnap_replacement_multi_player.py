from engine import GameState, PlayerState
from engine.replacements import resolve_replacement


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_replacement_choices_tagged_by_player():
    game_state = _build_state()
    game_state.turn.active_player_index = 0
    # Each player needs TWO matching effects to trigger a choice (otherwise one is auto-selected)
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "exile",
        "effect_id": "p0_a",
        "timestamp_order": 1,
        "player_id": 0,
    })
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "graveyard",
        "effect_id": "p0_b",
        "timestamp_order": 2,
        "player_id": 0,
    })
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "exile",
        "effect_id": "p1_a",
        "timestamp_order": 1,
        "player_id": 1,
    })
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "graveyard",
        "effect_id": "p1_b",
        "timestamp_order": 2,
        "player_id": 1,
    })

    resolve_replacement(game_state, "replace_draw", 0, "draw:event:player:0")
    resolve_replacement(game_state, "replace_draw", 1, "draw:event:player:1")

    pending = game_state.choices.get("pending", [])
    assert any(entry.get("player_id") == 0 for entry in pending)
    assert any(entry.get("player_id") == 1 for entry in pending)

