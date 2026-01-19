from engine import GameObject, GameState, PlayerState
from engine.continuous import apply_continuous_effects
from engine.zones import ZONE_BATTLEFIELD


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_set_oracle_text_layer():
    game_state = _build_state()
    obj = GameObject(
        id="obj",
        name="Test",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    obj.oracle_text = "base text"
    obj.temporary_effects.append({"type": "set_oracle_text", "text": "new text"})
    game_state.add_object(obj)

    apply_continuous_effects(game_state)
    assert obj.oracle_text == "new text"

    obj.temporary_effects = []
    apply_continuous_effects(game_state)
    assert obj.oracle_text == "base text"


def test_append_oracle_text_layer():
    game_state = _build_state()
    obj = GameObject(
        id="obj",
        name="Test",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    obj.oracle_text = "line1"
    obj.temporary_effects.append({"type": "append_oracle_text", "text": "line2"})
    game_state.add_object(obj)

    apply_continuous_effects(game_state)
    assert obj.oracle_text == "line1\nline2"


def test_control_change_updates_battlefield_lists():
    game_state = _build_state()
    obj = GameObject(
        id="obj",
        name="Test",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    obj.temporary_effects.append({"type": "set_controller", "controller_id": 1})
    game_state.add_object(obj)

    assert obj.id in game_state.get_player(0).battlefield
    apply_continuous_effects(game_state)

    assert obj.controller_id == 1
    assert obj.id not in game_state.get_player(0).battlefield
    assert obj.id in game_state.get_player(1).battlefield

