import pytest

from engine import GameObject, GameState, PlayerState
from engine.ability_registry import AbilityRegistry
from engine.events import Event
from engine.targets import validate_targets
from engine.turn import Phase, Step
from engine.zones import ZONE_BATTLEFIELD


def _build_game_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    game_state.turn.active_player_index = 0
    return game_state


def test_triggered_ability_pushes_stack_item():
    game_state = _build_game_state()
    creature = GameObject(
        id="creature_1",
        name="Test Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[
            {
                "rootNodeId": "trigger-1",
                "abilityType": "triggered",
                "nodes": [
                    {"id": "trigger-1", "type": "TRIGGER", "data": {"event": "enters_battlefield"}},
                    {"id": "effect-1", "type": "EFFECT", "data": {"type": "life", "amount": 1}},
                ],
                "edges": [{"from": "trigger-1", "to": "effect-1"}],
            }
        ],
    )
    game_state.add_object(creature)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="enters_battlefield", payload={"object_id": creature.id}))
    assert len(game_state.stack.items) == 1
    assert game_state.stack.items[0].kind == "ability_graph"


def test_validate_targets_rejects_hexproof():
    game_state = _build_game_state()
    protected = GameObject(
        id="hexproof_1",
        name="Hexproof Creature",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        keywords={"Hexproof"},
    )
    game_state.add_object(protected)

    context = type("Ctx", (), {})()
    context.targets = {"target": protected.id}
    context.controller_id = 0

    with pytest.raises(ValueError):
        validate_targets(game_state, context)


