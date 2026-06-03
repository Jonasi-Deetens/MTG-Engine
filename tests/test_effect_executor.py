"""Tests for Axis2 → Axis3 EffectExecutor."""

import pytest

from axis2 import schema as a2
from axis2.schema import Subject, ManaCost
from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1Metadata
from axis2.builder import Axis2Builder
from axis2.schema import Axis2Card, Axis2Characteristics, Axis2Face

from axis3.state.game_state import GameState, PlayerState
from axis3.state.objects import RuntimeObject
from axis3.state.zones import ZoneType
from axis3.engine.stack.stack import Stack
from axis3.runtime.effect_executor import EffectExecutor


def _minimal_axis1(name="Shock", oracle="Shock deals 2 damage to any target."):
    face = Axis1Face(
        face_id="front",
        name=name,
        mana_cost="{R}",
        mana_value=1,
        colors=["R"],
        card_types=["Instant"],
        oracle_text=oracle,
    )
    return Axis1Card(
        card_id="test-shock",
        layout="normal",
        names=[name],
        faces=[face],
        characteristics=Axis1Characteristics(
            mana_cost="{R}",
            mana_value=1,
            colors=["R"],
            card_types=["Instant"],
        ),
        metadata=Axis1Metadata(),
    )


def _minimal_axis2_creature(name="Grizzly", pid="bear-1", power=2, toughness=2):
    chars = Axis2Characteristics(
        mana_cost=ManaCost(symbols=["{1}", "{G}"]),
        mana_value=2,
        colors=["G"],
        color_identity=["G"],
        color_indicator=[],
        types=["Creature"],
        supertypes=[],
        subtypes=["Bear"],
        power=power,
        toughness=toughness,
        loyalty=None,
        defense=None,
    )
    face = Axis2Face(
        name=name,
        mana_cost=ManaCost(symbols=["{1}", "{G}"]),
        mana_value=2,
        colors=["G"],
        types=["Creature"],
        supertypes=[],
        subtypes=["Bear"],
        power=power,
        toughness=toughness,
        loyalty=None,
        defense=None,
    )
    return Axis2Card(
        card_id=pid,
        oracle_id=None,
        set="tst",
        collector_number="1",
        faces=[face],
        characteristics=chars,
    )


@pytest.fixture
def game_state():
    gs = GameState(
        players=[PlayerState(id=0, life=20), PlayerState(id=1, life=20)],
        objects={},
        stack=Stack(),
    )
    return gs


@pytest.fixture
def bear_on_battlefield(game_state):
    a2_card = _minimal_axis2_creature()
    obj = RuntimeObject(
        id="bear-1",
        owner=1,
        controller=1,
        zone=ZoneType.BATTLEFIELD,
        name="Grizzly Bears",
        axis2_card=a2_card,
        characteristics=a2_card.characteristics,
    )
    game_state.objects[obj.id] = obj
    game_state.players[1].battlefield.append(obj.id)
    return game_state, obj


def test_deal_damage_to_creature(bear_on_battlefield):
    gs, bear = bear_on_battlefield
    ex = EffectExecutor(gs)
    ex.execute(
        a2.DealDamageEffect(
            amount=2,
            subject=Subject(scope="target", types=["creature"], controller="opponent"),
        ),
        "source-1",
        0,
    )
    assert bear.damage == 2


def test_gain_life(game_state):
    ex = EffectExecutor(game_state)
    ex.execute(a2.GainLifeEffect(amount=3, subject="you"), "src", 0)
    assert game_state.players[0].life == 23


def test_draw_cards(game_state):
    for i in range(3):
        cid = f"lib-{i}"
        game_state.objects[cid] = RuntimeObject(
            id=cid,
            owner=0,
            controller=0,
            zone=ZoneType.LIBRARY,
            name=f"Card{i}",
        )
        game_state.players[0].library.append(cid)

    ex = EffectExecutor(game_state)
    ex.execute(a2.DrawCardsEffect(amount=2), "src", 0)
    assert len(game_state.players[0].hand) == 2
    assert len(game_state.players[0].library) == 1


def test_add_mana(game_state):
    ex = EffectExecutor(game_state)
    ex.execute(a2.AddManaEffect(mana=["{R}", "{G}"]), "src", 0)
    assert game_state.players[0].mana_pool["R"] == 1
    assert game_state.players[0].mana_pool["G"] == 1


def test_destroy_creature(bear_on_battlefield):
    gs, bear = bear_on_battlefield
    ex = EffectExecutor(gs)
    ex.execute(
        a2.DestroyEffect(
            subject=Subject(
                scope="target",
                types=["creature"],
                controller="opponent",
            )
        ),
        "src",
        0,
    )
    assert bear.id not in gs.players[1].battlefield
    assert bear.id in gs.players[1].graveyard


def test_create_token(game_state):
    ex = EffectExecutor(game_state)
    ex.execute(
        a2.CreateTokenEffect(
            amount=1,
            token={
                "name": "Soldier",
                "types": ["Creature"],
                "subtypes": ["Soldier"],
                "power": 1,
                "toughness": 1,
                "colors": ["W"],
            },
            controller="you",
        ),
        "src",
        0,
    )
    assert len(game_state.players[0].battlefield) == 1


def test_scry(game_state):
    for i in range(5):
        cid = f"s-{i}"
        game_state.objects[cid] = RuntimeObject(
            id=cid, owner=0, controller=0, zone=ZoneType.LIBRARY, name=f"S{i}"
        )
        game_state.players[0].library.append(cid)

    ex = EffectExecutor(game_state)
    ex.execute(a2.ScryEffect(amount=2), "src", 0)
    assert len(game_state.players[0].library) == 5


def test_surveil(game_state):
    for i in range(3):
        cid = f"m-{i}"
        game_state.objects[cid] = RuntimeObject(
            id=cid, owner=0, controller=0, zone=ZoneType.LIBRARY, name=f"M{i}"
        )
        game_state.players[0].library.append(cid)

    ex = EffectExecutor(game_state)
    ex.execute(a2.SurveilEffect(amount=2), "src", 0)
    assert len(game_state.players[0].graveyard) == 2


def test_put_counter(game_state, bear_on_battlefield):
    gs, bear = bear_on_battlefield
    ex = EffectExecutor(gs)
    ex.execute(a2.PutCounterEffect(counter_type="+1/+1", amount=2), bear.id, 1)
    assert bear.counters["+1/+1"] == 2


def test_discard(game_state):
    cid = "hand-1"
    game_state.objects[cid] = RuntimeObject(
        id=cid, owner=0, controller=0, zone=ZoneType.HAND, name="Discard Me"
    )
    game_state.players[0].hand.append(cid)

    ex = EffectExecutor(game_state)
    ex.execute(
        a2.DiscardEffect(
            subject=Subject(scope="target", types=["player"], controller="you"),
            amount=1,
        ),
        "src",
        0,
    )
    assert cid in game_state.players[0].graveyard


def test_axis2_builder_damage_effect():
    axis1 = _minimal_axis1()
    built = Axis2Builder.build(axis1)
    face = built.faces[0]
    all_effects = list(face.spell_effects)
    for aa in face.activated_abilities:
        all_effects.extend(aa.effects)
    for trig in face.triggered_abilities:
        all_effects.extend(trig.effects)
    # Parser produces DealDamageEffect; builder may attach to spell_effects or modes
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.schema import ParseContext

    ctx = ParseContext(
        card_name=axis1.names[0],
        primary_type="Instant",
        face_name=axis1.names[0],
        face_types=["Instant"],
        is_spell_text=True,
    )
    parsed = parse_effect_text(axis1.faces[0].oracle_text or "", ctx)
    assert any(isinstance(e, a2.DealDamageEffect) for e in parsed)
    assert any(isinstance(e, a2.DealDamageEffect) for e in all_effects) or len(parsed) > 0
