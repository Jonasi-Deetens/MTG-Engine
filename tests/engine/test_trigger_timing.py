from engine import AbilityRegistry, Event, GameObject, GameState, PlayerState, TurnManager
from engine.zones import ZONE_BATTLEFIELD


def _trigger_graph() -> dict:
    return {
        "rootNodeId": "t1",
        "abilityType": "triggered",
        "nodes": [
            {"id": "t1", "type": "TRIGGER", "data": {"event": "dies", "scope": "any"}},
            {"id": "e1", "type": "EFFECT", "data": {"type": "life", "amount": 0}},
        ],
        "edges": [{"from_": "t1", "to": "e1"}],
    }


def test_triggers_wait_for_priority():
    game_state = GameState(players=[PlayerState(id=0), PlayerState(id=1)])
    obj = GameObject(
        id="a",
        name="A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    assert not game_state.stack.items
    assert game_state.pending_triggers

    turn_manager = TurnManager(game_state)
    turn_manager._sync_priority(turn_manager.current_active_player_id())

    assert game_state.stack.items
    assert not game_state.pending_triggers

