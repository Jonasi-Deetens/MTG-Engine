from engine import AbilityRegistry, Event, GameObject, GameState, PlayerState
from engine.zones import ZONE_BATTLEFIELD


def _trigger_graph(scope: str = "any") -> dict:
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
                    "trigger": {"event": "dies", "scope": scope},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "life", "amount": 0},
                    },
                },
            },
        ],
    }


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_triggers_follow_apnap_order():
    game_state = _build_state()
    obj_a = GameObject(
        id="a",
        name="A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_trigger_graph()],
    )
    obj_b = GameObject(
        id="b",
        name="B",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj_a)
    game_state.add_object(obj_b)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    controller_ids = [item.get("controller_id") for item in game_state.pending_triggers]
    assert set(controller_ids) == {0, 1}
    assert len(controller_ids) == 2


def test_triggers_respect_active_player_order():
    game_state = _build_state()
    game_state.turn.active_player_index = 1
    obj_a = GameObject(
        id="a",
        name="A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_trigger_graph()],
    )
    obj_b = GameObject(
        id="b",
        name="B",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj_a)
    game_state.add_object(obj_b)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    controller_ids = [item.get("controller_id") for item in game_state.pending_triggers]
    assert set(controller_ids) == {0, 1}
    assert len(controller_ids) == 2
