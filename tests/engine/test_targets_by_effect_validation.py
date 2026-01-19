from engine import GameObject, GameState, PlayerState
from engine.state import ResolveContext
from engine.targets import validate_targets
from engine.zones import ZONE_HAND


def test_validate_targets_uses_targets_by_effect():
    game_state = GameState(players=[PlayerState(id=0)])
    obj = GameObject(
        id="obj",
        name="Not on Battlefield",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_HAND,
    )
    game_state.add_object(obj)
    context = ResolveContext(
        controller_id=0,
        targets_by_effect={"effect-1": {"target": obj.id}},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected targets_by_effect to be validated."
    except ValueError as exc:
        assert "effect-1" in str(exc)


def test_missing_required_target_by_effect_rejected():
    game_state = GameState(players=[PlayerState(id=0)])
    context = ResolveContext(
        controller_id=0,
        targets_by_effect={"effect-1": {}},
        required_targets_by_effect={"effect-1": ["target"]},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected missing required target to be rejected."
    except ValueError as exc:
        assert "missing target" in str(exc).lower()


def test_missing_required_global_target_rejected():
    game_state = GameState(players=[PlayerState(id=0)])
    context = ResolveContext(
        controller_id=0,
        targets={},
        required_targets_by_effect={"_global": ["target"]},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected missing required global target to be rejected."
    except ValueError as exc:
        assert "missing target" in str(exc).lower()


def test_distinct_targets_rejected_when_duplicates():
    game_state = GameState(players=[PlayerState(id=0)])
    context = ResolveContext(
        controller_id=0,
        targets={"targets": ["a", "a"]},
        distinct_targets_by_effect={"_global": ["target"]},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected duplicate targets to be rejected."
    except ValueError as exc:
        assert "distinct" in str(exc).lower()


def test_min_targets_rejected_when_too_few():
    game_state = GameState(players=[PlayerState(id=0)])
    context = ResolveContext(
        controller_id=0,
        targets={"targets": ["a"]},
        min_targets_by_effect={"_global": {"target": 2}},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected min targets violation."
    except ValueError as exc:
        assert "not enough targets" in str(exc).lower()


def test_optional_target_allows_zero_targets():
    game_state = GameState(players=[PlayerState(id=0)])
    context = ResolveContext(
        controller_id=0,
        targets={},
        min_targets_by_effect={"_global": {"target": 0}},
    )

    validate_targets(game_state, context)


def test_distinct_targets_rejects_duplicate_spell_and_object():
    game_state = GameState(players=[PlayerState(id=0)])
    context = ResolveContext(
        controller_id=0,
        targets={"target": "obj_1", "spell_target": "obj_1"},
        distinct_targets_by_effect={"_global": ["target"]},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected duplicate object/spell target to be rejected."
    except ValueError as exc:
        assert "distinct" in str(exc).lower()


def test_min_targets_counts_player_and_object():
    game_state = GameState(players=[PlayerState(id=0), PlayerState(id=1)])
    context = ResolveContext(
        controller_id=0,
        targets={"target": "obj_1", "target_player": 1},
        min_targets_by_effect={"_global": {"target": 2}},
    )

    validate_targets(game_state, context)


def test_distinct_fight_targets_rejected_when_same():
    game_state = GameState(players=[PlayerState(id=0), PlayerState(id=1)])
    context = ResolveContext(
        controller_id=0,
        targets_by_effect={
            "fight": {"yourCreature": "obj_1", "opponentCreature": "obj_1"},
        },
        distinct_targets_by_effect={"fight": ["yourCreature", "opponentCreature"]},
    )

    try:
        validate_targets(game_state, context)
        assert False, "Expected fight targets to require distinct objects."
    except ValueError as exc:
        assert "distinct" in str(exc).lower()

