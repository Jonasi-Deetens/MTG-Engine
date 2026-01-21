import pytest

from engine import GameObject, GameState, PlayerState, TurnManager, Phase, Step
from tests.engine.cost_helpers import mana_cost_data
from engine.rules import cast_spell
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    return game_state


def _basic_spell() -> GameObject:
    return GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )


def _ward_graph(costs: list[dict]) -> dict:
    return {
        "rootNodeId": "kw1",
        "abilityType": "keyword",
        "nodes": [
            {"id": "kw1", "type": "KEYWORD", "data": {"keyword": "ward", "costs": costs}},
        ],
        "edges": [],
    }


def test_ward_pay_life_auto():
    game_state = _build_state()
    warded = GameObject(
        id="warded",
        name="Warded",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    warded.ability_graphs = [_ward_graph([{"type": "life", "amount": 3}])]
    spell = _basic_spell()
    game_state.add_object(warded)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1
    starting_life = game_state.get_player(0).life

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        context={"targets": {"target": warded.id, "targets": [warded.id]}, "choices": {"ward_auto_pay": True}},
    )

    assert game_state.get_player(0).life == starting_life - 3


def test_ward_discard_requires_choice():
    game_state = _build_state()
    warded = GameObject(
        id="warded",
        name="Warded",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    warded.ability_graphs = [_ward_graph([{"type": "discard", "amount": 1}])]
    spell = _basic_spell()
    discard = GameObject(
        id="fodder",
        name="Fodder",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
    )
    game_state.add_object(warded)
    game_state.add_object(spell)
    game_state.add_object(discard)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1

    with pytest.raises(ValueError):
        cast_spell(
            game_state,
            turn_manager,
            player_id=0,
            object_id=spell.id,
            context={"targets": {"target": warded.id, "targets": [warded.id]}, "choices": {}},
        )

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        context={
            "targets": {"target": warded.id, "targets": [warded.id]},
            "choices": {"ward_payments": {warded.id: {"discard_id": discard.id}}},
        },
    )

    assert discard.zone == ZONE_GRAVEYARD


def test_ward_sacrifice_and_tap():
    game_state = _build_state()
    warded = GameObject(
        id="warded",
        name="Warded",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    warded.ability_graphs = [_ward_graph([{"type": "sacrifice", "card_type": "Creature"}])]
    warded_tap = GameObject(
        id="warded_tap",
        name="Warded Tap",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    warded_tap.ability_graphs = [_ward_graph([{"type": "tap", "card_type": "Creature"}])]
    sacrifice = GameObject(
        id="sac",
        name="Sacrifice",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    tapper = GameObject(
        id="tapper",
        name="Tapper",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    spell = _basic_spell()
    game_state.add_object(warded)
    game_state.add_object(warded_tap)
    game_state.add_object(sacrifice)
    game_state.add_object(tapper)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 2

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        context={
            "targets": {"target": warded.id, "targets": [warded.id]},
            "choices": {"ward_payments": {warded.id: {"sacrifice_id": sacrifice.id}}},
        },
    )

    assert sacrifice.zone == ZONE_GRAVEYARD

    # Resolve the first spell before casting the second (sorcery needs empty stack)
    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    second_spell = GameObject(
        id="spell_two",
        name="Spell Two",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(second_spell)
    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=second_spell.id,
        context={
            "targets": {"target": warded_tap.id, "targets": [warded_tap.id]},
            "choices": {"ward_payments": {warded_tap.id: {"tap_id": tapper.id}}},
        },
    )

    assert tapper.tapped is True


def test_ward_multiple_costs_and_discard_two():
    game_state = _build_state()
    warded = GameObject(
        id="warded_multi",
        name="Warded Multi",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    warded.ability_graphs = [
        _ward_graph([{"type": "mana", "cost": mana_cost_data("{1}")}]),
        _ward_graph([{"type": "life", "amount": 3}]),
    ]
    warded_disc = GameObject(
        id="warded_discard",
        name="Warded Discard",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    warded_disc.ability_graphs = [_ward_graph([{"type": "discard", "amount": 2}])]
    card_a = GameObject(
        id="card_a",
        name="Card A",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
    )
    card_b = GameObject(
        id="card_b",
        name="Card B",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
    )
    spell = _basic_spell()
    spell_two = GameObject(
        id="spell_multi",
        name="Spell Multi",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(warded)
    game_state.add_object(warded_disc)
    game_state.add_object(card_a)
    game_state.add_object(card_b)
    game_state.add_object(spell)
    game_state.add_object(spell_two)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 2
    starting_life = game_state.get_player(0).life

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        context={"targets": {"target": warded.id, "targets": [warded.id]}, "choices": {"ward_auto_pay": True}},
    )

    # Spell cost {G} + ward mana cost {1} = 2 mana, so 2G - 2 = 0G remaining
    # Ward life cost 3 = 40 - 3 = 37 life
    assert game_state.get_player(0).mana_pool.get("G", 0) == 0
    assert game_state.get_player(0).life == starting_life - 3

    # Resolve the first spell before casting the second (sorcery needs empty stack)
    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    # Add mana for the second spell
    game_state.get_player(0).mana_pool["G"] = 1

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell_two.id,
        context={
            "targets": {"target": warded_disc.id, "targets": [warded_disc.id]},
            "choices": {"ward_payments": {warded_disc.id: {"discard_ids": [card_a.id, card_b.id]}}},
        },
    )

    assert card_a.zone == ZONE_GRAVEYARD
    assert card_b.zone == ZONE_GRAVEYARD

