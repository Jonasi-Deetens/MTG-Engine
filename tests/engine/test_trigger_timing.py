from engine import AbilityRegistry, Event, GameObject, GameState, PlayerState, TurnManager
from engine.zones import ZONE_BATTLEFIELD


def _trigger_graph() -> dict:
    return {
        "id": "graph-1",
        "sourceKind": "permanent",
        "steps": [
            {
                "id": "step-1",
                "effect": {
                    "id": "eff-1",
                    "initiation": "triggered",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "trigger": {"event": "dies", "scope": "any"},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "life", "amount": 0},
                    },
                },
            },
        ],
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
        effect_graphs=[_trigger_graph()],
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

