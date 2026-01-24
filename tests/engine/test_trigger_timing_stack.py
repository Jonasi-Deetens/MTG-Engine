from engine import AbilityRegistry, Event, GameObject, GameState, PlayerState, TurnManager
from engine.stack import StackItem
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD


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


def test_triggers_from_resolution_go_on_stack_before_priority():
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
    turn_manager = TurnManager(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))
    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim2"}))

    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    controller_ids = [item.controller_id for item in game_state.stack.items]
    assert set(controller_ids) == {0, 1}
    assert len(controller_ids) == 4


def test_priority_returns_to_active_after_pending_triggers():
    """Test that priority returns to active player after pending triggers are placed on stack."""
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

    # Both players pass - spell resolves, then pending triggers are placed
    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    # After pending triggers are placed on stack, priority returns to active player
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
        effect_graphs=[_trigger_graph()],
    )
    game_state.add_object(obj)
    AbilityRegistry(game_state)
    turn_manager = TurnManager(game_state)

    game_state.event_bus.publish(Event(type="dies", payload={"object_id": "victim"}))
    turn_manager.handle_player_pass(turn_manager.current_active_player_id())

    assert game_state.stack.items
    assert (game_state.turn.phase, game_state.turn.step) == ("precombat_main", "precombat_main")