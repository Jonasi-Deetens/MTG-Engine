# tests/test_axis3_integration.py
import pytest

from axis2.schema import Axis2Characteristics
from axis3.state.game_state import GameState, PlayerState
from axis3.state.objects import RuntimeObject
from axis3.state.zones import ZoneType as Zone
from axis3.engine.loader.loader import create_runtime_object
from axis3.rules.sba.checker import run_sbas
from axis3.rules.events.types import EventType
from axis3.engine.stack.resolver import resolve_stack
from axis3.rules.events.event import Event

# Dummy Axis1 and Axis2 objects for testing
class DummyAxis1Card:
    def __init__(
        self,
        name="TestCard",
        power=None,
        toughness=None,
        types=None,
        colors=None,
        card_id=None,
        mana_cost="{0}",
        oracle_text="",
    ):
        self.names = [name]
        self.faces = [self]

        # Axis1 fields expected by Axis2 builder
        self.card_id = card_id or name + "-001"
        self.mana_cost = mana_cost
        self.mana_value = 0
        self.oracle_text = oracle_text

        # Types and colors
        self.card_types = types or []
        self.supertypes = []
        self.subtypes = []
        self.colors = colors or []
        self.color_indicator = []

        # P/T
        self.power = power
        self.toughness = toughness


class DummyAxis2Card:
    def __init__(self, axis1_card=None):
        from axis3.rules.costs.mana import ManaCost

        self.axis1_card = axis1_card

        self.characteristics = Axis2Characteristics(
            mana_cost=ManaCost(),
            mana_value=0,
            colors=[],
            color_identity=[],
            color_indicator=[],
            types=["Creature"],
            supertypes=[],
            subtypes=[],
            power=3,
            toughness=3,
        )

        # Empty but structurally correct
        self.actions = {}
        self.triggers = []
        self.zone_permissions = []
        self.global_restrictions = []
        self.conditions = []
        self.action_replacements = []
        self.action_preventions = []
        self.action_modifiers = []
        self.mandatory_actions = []
        self.choice_constraints = []
        self.limits = []
        self.visibility_constraints = []
        self.keywords = []
        self.static_effects = []
        self.replacement_effects = []
        self.modes = []
        self.mode_choice = None

        # Must be a list of objects with .cost and .effect
        self.activated_abilities = []


@pytest.fixture
def game_state():
    # Create two players with empty decks
    gs = GameState(
        players=[PlayerState(id=0), PlayerState(id=1)],
        objects={},
    )

    # Add a creature for each player
    a1 = DummyAxis1Card(name="P1Creature", power=3, toughness=3, types=["Creature"], card_id="P1Creature-001")
    a2 = DummyAxis2Card()

    c1 = create_runtime_object(a1, a2, owner_id=0, zone=Zone.BATTLEFIELD, game_state=gs)
    gs.objects[c1.id] = c1
    gs.players[0].battlefield.append(c1.id)

    a3 = DummyAxis1Card(name="P2Creature", power=2, toughness=2, types=["Creature"], card_id="P2Creature-001")
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

    c1 = gs.objects[gs.players[0].battlefield[0]]

    # Apply a continuous effect that sets toughness to 0
    from axis3.abilities.static import RuntimeContinuousEffect

    def applies_to(gs_inner, obj_id):
        return obj_id == c1.id

    def mod_toughness(gs_inner, obj_id, current):
        return 0  # force toughness to 0

    ce = RuntimeContinuousEffect(
        source_id=c1.id,
        layer=7,
        sublayer="7b",
        applies_to=applies_to,
        modify_toughness=mod_toughness,
    )
    gs.continuous_effects.append(ce)

    # Run SBAs
    run_sbas(gs)

    assert c1.zone == Zone.GRAVEYARD
    assert c1.id in gs.players[0].graveyard

def test_trigger_registration(game_state):
    gs = game_state
    c1 = gs.objects[gs.players[0].battlefield[0]]

    # Add a dummy triggered ability that sets a flag
    triggered_flag = {"fired": False}
    def callback(gs, event):
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
            self.cost = [] # must be iterable            
            self.effect = [self._effect] # list of callables 
            
        def _effect(self, gs_inner, source_id, controller): 
            setattr(gs_inner, "dummy_flag", True)

    from axis3.engine.translate.activated_builder import register_runtime_activated_abilities
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
            self.cost = [] # must be iterable            
            self.effect = [self._effect] # list of callables 
            
        def _effect(self, gs_inner, source_id, controller): 
            setattr(gs_inner, "dummy_flag", True)

    c1.axis2_card.activated_abilities = [DummyActivated()]
    from axis3.engine.translate.activated_builder import register_runtime_activated_abilities
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
            self.cost = [] # must be iterable            
            self.effect = [self._effect] # list of callables 
            
        def _effect(self, gs_inner, source_id, controller): 
            setattr(gs_inner, "dummy_flag", True)

    c1.axis2_card.activated_abilities = [DummyActivated()]
    from axis3.engine.translate.activated_builder import register_runtime_activated_abilities
    register_runtime_activated_abilities(gs, c1)

    raa = c1.runtime_activated_abilities[0]
    raa.activate(gs)

    # Stack has the ability
    from axis3.engine.stack.resolver import resolve_stack
    resolve_stack(gs)

    # After resolution, effect should have run
    assert getattr(gs, "dummy_flag", False) is True
    # Stack should now be empty
    assert gs.stack.is_empty()

def test_life_change_event_pipeline(game_state):
    gs = game_state

    from axis3.rules.events.event import Event
    from axis3.rules.events.types import EventType

    # Snapshot before
    old_life = gs.players[0].life

    # This should apply one life change and stop (no infinite loop)
    gs.event_bus.publish(Event(
        type=EventType.LIFE_CHANGE,
        payload={"player_id": 0, "amount": -3}
    ))

    # Life should be reduced by 3
    assert gs.players[0].life == old_life - 3
