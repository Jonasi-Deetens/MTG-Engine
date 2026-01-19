from engine import GameObject, GameState, PlayerState
from engine.replacements import resolve_replacement
from engine.zones import ZONE_BATTLEFIELD


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_replacement_choice_queued_for_active_player():
    game_state = _build_state()
    obj = GameObject(
        id="obj",
        name="Obj",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    game_state.add_object(obj)
    game_state.turn.active_player_index = 0
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "exile",
        "effect_id": "r1",
        "timestamp_order": 1,
        "player_id": 0,
    })
    game_state.replacement_effects.append({
        "type": "replace_draw",
        "replacement_zone": "graveyard",
        "effect_id": "r2",
        "timestamp_order": 2,
        "player_id": 0,
    })

    resolve_replacement(game_state, "replace_draw", 0, "draw:event:player:0")

    pending = game_state.choices.get("pending", [])
    assert pending
    assert pending[0]["player_id"] == 0

