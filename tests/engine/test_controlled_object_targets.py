from engine import GameObject, GameState, PlayerState
from engine.effects import EffectResolver
from engine.state import ResolveContext
from engine.zones import ZONE_BATTLEFIELD


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    return game_state


def test_effect_targets_creatures_you_control():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    creature_you = GameObject(
        id="c1",
        name="You Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    creature_opp = GameObject(
        id="c2",
        name="Opp Creature",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(creature_you)
    game_state.add_object(creature_opp)
    context = ResolveContext(controller_id=0)

    result = resolver.apply(
        {"type": "change_power_toughness", "powerChange": 1, "toughnessChange": 1, "target": "creatures_you_control"},
        context,
    )

    assert result["type"] == "change_power_toughness"
    assert len(result["results"]) == 1
    assert result["results"][0]["object_id"] == creature_you.id


def test_effect_targets_creatures_opponents_control():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    creature_you = GameObject(
        id="c1",
        name="You Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    creature_opp = GameObject(
        id="c2",
        name="Opp Creature",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(creature_you)
    game_state.add_object(creature_opp)
    context = ResolveContext(controller_id=0)

    result = resolver.apply(
        {"type": "change_power_toughness", "powerChange": -1, "toughnessChange": -1, "target": "creatures_opponents_control"},
        context,
    )

    assert result["type"] == "change_power_toughness"
    assert len(result["results"]) == 1
    assert result["results"][0]["object_id"] == creature_opp.id


def test_effect_targets_artifacts_you_control():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    artifact_you = GameObject(
        id="a1",
        name="You Artifact",
        owner_id=0,
        controller_id=0,
        types=["Artifact"],
        zone=ZONE_BATTLEFIELD,
    )
    artifact_opp = GameObject(
        id="a2",
        name="Opp Artifact",
        owner_id=1,
        controller_id=1,
        types=["Artifact"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(artifact_you)
    game_state.add_object(artifact_opp)
    context = ResolveContext(controller_id=0)

    result = resolver.apply(
        {"type": "destroy", "target": "artifacts_you_control"},
        context,
    )

    assert result["type"] == "destroy"
    assert len(result["results"]) == 1
    assert result["results"][0]["object_id"] == artifact_you.id


def test_target_object_scope_opponent_rejects_controller():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    creature_you = GameObject(
        id="c1",
        name="You Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(creature_you)
    context = ResolveContext(controller_id=0, targets={"target": creature_you.id, "target_object_scope": "opponent_control"})

    result = resolver.apply(
        {"type": "change_power_toughness", "powerChange": 1, "toughnessChange": 1, "target": "target_creature_opponents_control"},
        context,
    )

    assert result["type"] == "change_power_toughness"
    assert result["status"] == "no_target"
