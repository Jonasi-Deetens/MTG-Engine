import pytest

from engine import GameObject, GameState, PlayerState, TurnManager
from tests.engine.cost_helpers import mana_cost_data
from engine.rules import cast_spell, prepare_cast
from engine.zones import ZONE_EXILE, ZONE_GRAVEYARD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def test_cast_spell_with_free_alt_cost():
    game_state = _build_state()
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{3}{U}",
    )
    graph = {
        "rootNodeId": "kw1",
        "abilityType": "keyword",
        "nodes": [
            {"id": "kw1", "type": "KEYWORD", "data": {"keyword": "free"}},
        ],
        "edges": [],
    }
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)

    result = prepare_cast(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={"choices": {"alternative_cost_tag": "free"}},
    )

    assert result.get("cost", {}).get("generic") == 0

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={"choices": {"alternative_cost_tag": "free"}},
    )

    assert game_state.stack.items


def test_cast_spell_with_mana_alt_cost():
    game_state = _build_state()
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{3}{U}",
    )
    graph = {
        "rootNodeId": "kw1",
        "abilityType": "keyword",
        "nodes": [
            {
                "id": "kw1",
                "type": "KEYWORD",
                "data": {"keyword": "alternative_cost", "costs": [{"type": "mana", "cost": mana_cost_data("{1}{R}")}]},
            },
        ],
        "edges": [],
    }
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["R"] = 1
    game_state.get_player(0).mana_pool["C"] = 1

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={"choices": {"alternative_cost_tag": "{1}{R}"}},
    )

    assert game_state.get_player(0).mana_pool.get("R", 0) == 0
    assert game_state.stack.items


def test_cast_spell_with_flashback_from_graveyard():
    game_state = _build_state()
    spell = GameObject(
        id="flashback_spell",
        name="Flashback Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_GRAVEYARD,
        mana_cost="{3}{U}",
    )
    graph = {
        "rootNodeId": "kw1",
        "abilityType": "keyword",
        "nodes": [
            {
                "id": "kw1",
                "type": "KEYWORD",
                "data": {"keyword": "flashback", "costs": [{"type": "mana", "cost": mana_cost_data("{1}{R}")}]},
            },
        ],
        "edges": [],
    }
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["R"] = 1
    game_state.get_player(0).mana_pool["C"] = 1

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={"choices": {"alternative_cost_tag": "flashback:{1}{R}"}},
    )

    assert game_state.stack.items
    assert game_state.stack.items[-1].payload.get("destination_zone") == ZONE_EXILE


def test_cast_spell_with_escape_exiles_cards():
    game_state = _build_state()
    spell = GameObject(
        id="escape_spell",
        name="Escape Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_GRAVEYARD,
        mana_cost="{4}{R}",
    )
    graph = {
        "rootNodeId": "kw1",
        "abilityType": "keyword",
        "nodes": [
            {
                "id": "kw1",
                "type": "KEYWORD",
                "data": {"keyword": "escape", "costs": [{"type": "mana", "cost": mana_cost_data("{2}{R}")}], "number": 2},
            },
        ],
        "edges": [],
    }
    grave_a = GameObject(
        id="grave_a",
        name="Grave A",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_GRAVEYARD,
    )
    grave_b = GameObject(
        id="grave_b",
        name="Grave B",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_GRAVEYARD,
    )
    game_state.add_object(spell)
    game_state.add_object(grave_a)
    game_state.add_object(grave_b)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["R"] = 1
    game_state.get_player(0).mana_pool["C"] = 2

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={
            "choices": {
                "alternative_cost_tag": "escape:{2}{R}",
                "alternative_cost_payments": {
                    spell.id: {"exile_ids": [grave_a.id, grave_b.id]},
                },
            }
        },
    )

    assert game_state.stack.items
    assert game_state.stack.items[-1].payload.get("destination_zone") == ZONE_EXILE
    assert grave_a.zone == ZONE_EXILE
    assert grave_b.zone == ZONE_EXILE


def test_cast_spell_with_jump_start_discards():
    game_state = _build_state()
    spell = GameObject(
        id="jump_spell",
        name="Jump Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_GRAVEYARD,
        mana_cost="{1}{R}",
    )
    graph = {
        "rootNodeId": "kw1",
        "abilityType": "keyword",
        "nodes": [
            {"id": "kw1", "type": "KEYWORD", "data": {"keyword": "jump-start"}},
        ],
        "edges": [],
    }
    discard = GameObject(
        id="discard_card",
        name="Discard",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
    )
    game_state.add_object(spell)
    game_state.add_object(discard)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["R"] = 1
    game_state.get_player(0).mana_pool["C"] = 1

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={
            "choices": {
                "alternative_cost_tag": "jump-start",
                "alternative_cost_payments": {spell.id: {"discard_id": discard.id}},
            }
        },
    )

    assert discard.zone == ZONE_GRAVEYARD
    assert game_state.stack.items[-1].payload.get("destination_zone") == ZONE_EXILE
