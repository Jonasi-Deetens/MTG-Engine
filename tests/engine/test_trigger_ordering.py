from engine import AbilityRegistry, Event, GameObject, GameState, PlayerState
from engine.zones import ZONE_BATTLEFIELD


def _trigger_graph(scope: str = "any") -> dict:
    return {
        "rootNodeId": "t1",
        "abilityType": "triggered",
        "nodes": [
            {"id": "t1", "type": "TRIGGER", "data": {"event": "dies", "scope": scope}},
            {"id": "e1", "type": "EFFECT", "data": {"type": "life", "amount": 0}},
        ],
        "edges": [{"from_": "t1", "to": "e1"}],
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
        ability_graphs=[_trigger_graph()],
    )
    obj_b = GameObject(
        id="b",
        name="B",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj_a)
    game_state.add_object(obj_b)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    assert [item.controller_id for item in game_state.stack.items] == [0, 1]


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
        ability_graphs=[_trigger_graph()],
    )
    obj_b = GameObject(
        id="b",
        name="B",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj_a)
    game_state.add_object(obj_b)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    assert [item.controller_id for item in game_state.stack.items] == [1, 0]


def test_trigger_order_choices_apnap_sorted():
    game_state = _build_state()
    game_state.turn.active_player_index = 0
    obj_a = GameObject(
        id="a",
        name="A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph()],
    )
    obj_b = GameObject(
        id="b",
        name="B",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj_a)
    game_state.add_object(obj_b)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    pending = game_state.choices.get("pending", [])
    trigger_entries = [entry for entry in pending if entry.get("type") == "trigger_order"]
    assert trigger_entries
    assert trigger_entries[0]["player_id"] == 0


def test_trigger_order_choice_respected_within_player():
    game_state = _build_state()
    obj_a = GameObject(
        id="a",
        name="A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph()],
    )
    obj_b = GameObject(
        id="b",
        name="B",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj_a)
    game_state.add_object(obj_b)
    registry = AbilityRegistry(game_state)

    entries = [entry for entry in registry.registered if entry.controller_id == 0]
    assert len(entries) == 2
    key_a = registry._entry_key(entries[0])
    key_b = registry._entry_key(entries[1])
    game_state.choices["trigger_order:0:dies"] = [key_b, key_a]

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    assert game_state.stack.items[0].payload.get("source_object_id") == entries[1].source_id
