from engine import GameState, PlayerState
from engine.replacements import resolve_replacements_for_players


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_resolve_replacements_for_players_apnap_order():
    game_state = _build_state()
    game_state.turn.active_player_index = 1
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "exile",
        "effect_id": "p0",
        "timestamp_order": 1,
        "player_id": 0,
    })
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "graveyard",
        "effect_id": "p1",
        "timestamp_order": 1,
        "player_id": 1,
    })

    results = resolve_replacements_for_players(
        game_state,
        "replace_draw",
        [0, 1],
        "draw:event:player:",
    )

    assert [player_id for player_id, _ in results] == [1, 0]

