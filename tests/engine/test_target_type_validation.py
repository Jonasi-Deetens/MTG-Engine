from engine import GameObject, GameState, PlayerState
from engine.state import ResolveContext
from engine.targets import validate_targets
from engine.zones import ZONE_BATTLEFIELD


def test_target_object_types_rejects_mismatched_type():
    game_state = GameState(players=[PlayerState(id=0)])
    obj = GameObject(
        id="obj",
        name="NonCreature",
        owner_id=0,
        controller_id=0,
        types=["Artifact"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(obj)
    context = ResolveContext(
        controller_id=0,
        targets={"target": obj.id, "target_object_types": ["Creature"]},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected type constraint to reject non-creature target."
    except ValueError as exc:
        assert "required types" in str(exc).lower()

