from engine import GameState, PlayerState
from engine.state import ResolveContext
from engine.targets import validate_targets


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_target_scope_opponent_rejects_controller():
    game_state = _build_state()
    context = ResolveContext(
        controller_id=0,
        targets={"target_player": 0, "target_scope": "opponent"},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected opponent scope to reject controller as target."
    except ValueError as exc:
        assert "illegal target" in str(exc).lower()


def test_target_scope_controller_accepts_controller():
    game_state = _build_state()
    context = ResolveContext(
        controller_id=0,
        targets={"target_player": 0, "target_scope": "controller"},
    )

    validate_targets(game_state, context)


def test_target_object_scope_opponent_rejects_controller_object():
    from engine import GameObject
    from engine.zones import ZONE_BATTLEFIELD

    game_state = _build_state()
    obj = GameObject(
        id="obj",
        name="Owned",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(obj)
    context = ResolveContext(
        controller_id=0,
        targets={"target": obj.id, "target_object_scope": "opponent_control"},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected opponent control scope to reject controller object."
    except ValueError as exc:
        # Accept either "illegal" or "not controlled by an opponent"
        err_msg = str(exc).lower()
        assert "illegal" in err_msg or "not controlled by an opponent" in err_msg

