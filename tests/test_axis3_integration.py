# tests/test_axis3_integration.py
import pytest

from axis3.state.game_state import GameState, PlayerState
from axis3.state.objects import RuntimeObject
from axis3.state.zones import ZoneType as Zone
from axis3.translate.loader import create_runtime_object
from axis3.rules.sba.checker import run_sbas
from axis3.rules.layers.system import evaluate_characteristics
from axis3.rules.events.types import EventType
from axis3.rules.stack.resolver import resolve_stack
from axis3.rules.events.event import Event
# Dummy Axis1 and Axis2 objects for testing
class DummyAxis1Card:
    def __init__(self, name="TestCard", power=None, toughness=None, types=None, colors=None):
        self.names = [name]
        self.faces = [self]
        self.types = types or []
        self.supertypes = []
        self.subtypes = []
        self.power = power
        self.toughness = toughness
        self.colors = colors or []

class DummyAxis2Card:
    def __init__(self, triggers=None, activated_abilities=None, continuous_effects=None, replacement_effects=None):
        self.triggers = triggers or []
        self.activated_abilities = activated_abilities or []
        self.continuous_effects = continuous_effects or []
        self.replacement_effects = replacement_effects or []

@pytest.fixture
def game_state():
    # Create two players with empty decks
    gs = GameState(
        players=[PlayerState(id=0), PlayerState(id=1)],
        objects={},
    )

    # Add a creature for each player
    a1 = DummyAxis1Card(name="P1Creature", power=3, toughness=3, types=["Creature"])
    a2 = DummyAxis2Card()

    c1 = create_runtime_object(a1, a2, owner_id=0, zone=Zone.BATTLEFIELD, game_state=gs)
    gs.objects[c1.id] = c1
    gs.players[0].battlefield.append(c1.id)

    a3 = DummyAxis1Card(name="P2Creature", power=2, toughness=2, types=["Creature"])
    a4 = DummyAxis2Card()

    c2 = create_runtime_object(a3, a4, owner_id=1, zone=Zone.BATTLEFIELD, game_state=gs)
    gs.objects[c2.id] = c2
    gs.players[1].battlefield.append(c2.id)

    return gs

def test_sba_creature_death(game_state):
    gs = game_state

    # Inflict lethal damage on P2Creature
    c2 = gs.objects[gs.players[1].battlefield[0]]
    c2.damage = 3

    # Run SBAs
    run_sbas(gs)

    # Creature should be in graveyard
    assert c2.zone == Zone.GRAVEYARD
    assert c2.id in gs.players[1].graveyard

def test_zero_toughness_death(game_state):
    gs = game_state

    # Set toughness to 0
    c1 = gs.objects[gs.players[0].battlefield[0]]
    c1.characteristics.toughness = 0

    run_sbas(gs)

    assert c1.zone == Zone.GRAVEYARD
    assert c1.id in gs.players[0].graveyard

def test_trigger_registration(game_state):
    gs = game_state
    c1 = gs.objects[gs.players[0].battlefield[0]]

    # Add a dummy triggered ability that sets a flag
    triggered_flag = {"fired": False}
    def callback(event):
        triggered_flag["fired"] = True

    # Manually subscribe
    gs.event_bus.subscribe(EventType.ENTERS_BATTLEFIELD, callback)

    # Fire the event
    gs.event_bus.publish(Event(
        type=EventType.ENTERS_BATTLEFIELD,
        payload={"obj_id": c1.id, "controller": c1.controller}
    ))

    assert triggered_flag["fired"] is True

def test_continuous_effect_applied(game_state):
    gs = game_state
    c1 = gs.objects[gs.players[0].battlefield[0]]

    # Add a +1/+1 continuous effect
    def applies_to(gs_inner, obj_id):
        return obj_id == c1.id

    def mod_power(gs_inner, obj_id, current):
        return current + 1

    def mod_toughness(gs_inner, obj_id, current):
        return current + 1

    from axis3.abilities.static import RuntimeContinuousEffect
    ce = RuntimeContinuousEffect(
        source_id=c1.id,
        layer=7,
        sublayer="7b",
        applies_to=applies_to,
        modify_power=mod_power,
        modify_toughness=mod_toughness,
    )
    gs.continuous_effects.append(ce)

    ec = gs.layers.evaluate(c1.id)
    assert ec.power == c1.characteristics.power + 1
    assert ec.toughness == c1.characteristics.toughness + 1

def test_replacement_effect(game_state):
    gs = game_state
    c1 = gs.objects[gs.players[0].battlefield[0]]

    # Add replacement effect: dies -> exile
    from axis3.rules.replacement.types import ReplacementEffect
    repl = ReplacementEffect(
        source_id=c1.id,
        applies_to="zone_change",
        condition=lambda e, obj_id=c1.id: (
            e.type == EventType.ZONE_CHANGE and
            e.payload.get("obj_id") == obj_id and
            e.payload.get("to_zone") == Zone.GRAVEYARD
        ),
        apply=lambda e: Event(
            type=e.type,
            payload={**e.payload, "to_zone": Zone.EXILE}
        )
    )
    gs.replacement_effects.append(repl)

    # Inflict lethal damage
    c1.damage = c1.characteristics.toughness
    # Publish a ZONE_CHANGE event via EventBus
    gs.event_bus.publish(Event(
        type=EventType.ZONE_CHANGE,
        payload={
            "obj_id": c1.id,
            "from_zone": Zone.BATTLEFIELD,
            "to_zone": Zone.GRAVEYARD,
            "controller": c1.controller,
            "cause": "lethal_damage"
        }
    ))

    assert c1.zone == Zone.EXILE
    assert c1.id not in gs.players[0].graveyard

def test_activated_ability_registration(game_state):
    gs = game_state
    c1 = gs.objects[gs.players[0].battlefield[0]]

    # Add dummy activated ability
    class DummyActivated:
        def __init__(self):
            self.cost = None
            self.effect = lambda gs_inner: setattr(gs_inner, "dummy_flag", True)

    from axis3.translate.activated_builder import register_runtime_activated_abilities
    c1.axis2_card.activated_abilities = [DummyActivated()]
    register_runtime_activated_abilities(gs, c1)

    print(c1.runtime_activated_abilities)

    assert hasattr(c1, "runtime_activated_abilities")
    assert len(c1.runtime_activated_abilities) == 1

def test_runtime_activated_ability_activation(game_state):
    gs = game_state
    c1 = gs.objects[gs.players[0].battlefield[0]]

    class DummyActivated:
        def __init__(self):
            self.cost = None
            self.effect = lambda gs_inner, source_id, controller: setattr(gs_inner, "dummy_flag", True)

    c1.axis2_card.activated_abilities = [DummyActivated()]
    from axis3.translate.activated_builder import register_runtime_activated_abilities
    register_runtime_activated_abilities(gs, c1)

    raa = c1.runtime_activated_abilities[0]

    # Activate it
    raa.activate(gs)

    # It should push to the stack
    assert len(gs.stack.items) == 1
    stack_item = gs.stack.peek()
    assert stack_item.activated_ability == raa

def test_runtime_activated_ability_resolution(game_state):
    gs = game_state
    c1 = gs.objects[gs.players[0].battlefield[0]]

    class DummyActivated:
        def __init__(self):
            self.cost = None
            self.effect = lambda gs_inner, source_id, controller: setattr(gs_inner, "dummy_flag", True)

    c1.axis2_card.activated_abilities = [DummyActivated()]
    from axis3.translate.activated_builder import register_runtime_activated_abilities
    register_runtime_activated_abilities(gs, c1)

    raa = c1.runtime_activated_abilities[0]
    raa.activate(gs)

    # Stack has the ability
    from axis3.rules.stack.resolver import resolve_stack
    resolve_stack(gs)

    # After resolution, effect should have run
    assert getattr(gs, "dummy_flag", False) is True
    # Stack should now be empty
    assert gs.stack.is_empty()

