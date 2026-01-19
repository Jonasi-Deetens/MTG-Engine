from engine import AbilityRegistry, Event, GameObject, GameState, PlayerState, TurnManager
from engine.stack import StackItem
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD


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


def test_triggers_from_resolution_go_on_stack_before_priority():
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
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_GRAVEYARD,
    )
    game_state.add_object(obj)
    game_state.add_object(spell)
    AbilityRegistry(game_state)
    turn_manager = TurnManager(game_state)

    game_state.stack.push(StackItem(kind="spell", payload={"object_id": spell.id, "destination_zone": ZONE_GRAVEYARD}, controller_id=0))

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))
    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    assert game_state.stack.items


def test_multiple_pending_triggers_between_passes():
    game_state = GameState(players=[PlayerState(id=0), PlayerState(id=1)])
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
    turn_manager = TurnManager(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))
    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim2"}))

    assert game_state.pending_triggers
    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    assert len(game_state.stack.items) == 4


def test_pending_triggers_apnap_ordered_before_priority():
    game_state = GameState(players=[PlayerState(id=0), PlayerState(id=1)])
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
    turn_manager = TurnManager(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))
    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim2"}))

    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    assert [item.controller_id for item in game_state.stack.items] == [1, 0, 1, 0]


def test_trigger_order_choice_respected_when_pending():
    game_state = GameState(players=[PlayerState(id=0), PlayerState(id=1)])
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
    turn_manager = TurnManager(game_state)

    entries = [entry for entry in registry.registered if entry.controller_id == 0]
    key_a = registry._entry_key(entries[0])
    key_b = registry._entry_key(entries[1])
    game_state.choices["trigger_order:0:dies"] = [key_b, key_a]

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))
    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    assert game_state.stack.items[0].payload.get("source_object_id") == entries[1].source_id


def test_priority_returns_to_active_after_pending_triggers():
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
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_GRAVEYARD,
    )
    game_state.add_object(obj)
    game_state.add_object(spell)
    AbilityRegistry(game_state)
    turn_manager = TurnManager(game_state)

    game_state.stack.push(StackItem(kind="spell", payload={"object_id": spell.id, "destination_zone": ZONE_GRAVEYARD}, controller_id=0))
    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))

    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    assert turn_manager.priority.current == turn_manager.current_active_player_id()


def test_pending_triggers_prevent_step_advance():
    game_state = GameState(players=[PlayerState(id=0), PlayerState(id=1)])
    game_state.turn.phase = "precombat_main"
    game_state.turn.step = "precombat_main"
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
    turn_manager = TurnManager(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))
    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    assert game_state.stack.items
    assert (game_state.turn.phase, game_state.turn.step) == ("precombat_main", "precombat_main")