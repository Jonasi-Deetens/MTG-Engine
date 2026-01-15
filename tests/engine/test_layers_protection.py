import pytest

from engine import GameObject, GameState, PlayerState
from engine.continuous import apply_continuous_effects
from engine.damage import apply_damage_to_object
from engine.sba import apply_state_based_actions
from engine.targets import validate_targets
from engine.zones import ZONE_BATTLEFIELD


def _build_game_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_layers_apply_keywords_and_counters():
    game_state = _build_game_state()
    creature = GameObject(
        id="creature_1",
        name="Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
        base_power=2,
        base_toughness=2,
        base_keywords=set(["Vigilance"]),
        keywords=set(["Vigilance"]),
    )
    creature.counters["+1/+1"] = 1
    creature.temporary_effects.append({"type": "add_keyword", "keyword": "Flying"})
    game_state.add_object(creature)

    apply_continuous_effects(game_state)
    assert creature.power == 3
    assert creature.toughness == 3
    assert "Flying" in creature.keywords


def test_indestructible_prevents_sba_death():
    game_state = _build_game_state()
    creature = GameObject(
        id="creature_2",
        name="Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
        base_power=2,
        base_toughness=2,
        base_keywords=set(["Indestructible"]),
        keywords=set(["Indestructible"]),
    )
    creature.damage = 3
    game_state.add_object(creature)

    apply_state_based_actions(game_state)
    assert creature.zone == ZONE_BATTLEFIELD


def test_protection_prevents_damage_and_targeting():
    game_state = _build_game_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        colors=["R"],
    )
    target = GameObject(
        id="target",
        name="Target",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        protections=set(["R"]),
    )
    game_state.add_object(source)
    game_state.add_object(target)

    apply_damage_to_object(game_state, source, target, 3)
    assert target.damage == 0

    context = type("Ctx", (), {})()
    context.targets = {"target": target.id}
    context.controller_id = 0
    context.source_id = source.id
    context.choices = {}

    with pytest.raises(ValueError):
        validate_targets(game_state, context)


