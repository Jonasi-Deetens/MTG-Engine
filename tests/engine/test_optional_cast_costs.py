import pytest

from engine import AbilityGraphRuntimeAdapter, GameObject, GameState, PlayerState, ResolveContext, TurnManager, Phase, Step
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


def _spell_graph_with_keywords(keywords: list[dict]) -> dict:
    return {
        "rootNodeId": "e1",
        "abilityType": "static",
        "nodes": [
            {"id": "e1", "type": "EFFECT", "data": {"type": "lose_life", "amount": 1, "target": "player"}},
            *keywords,
        ],
        "edges": [],
    }


def test_kicker_optional_cost_sets_kicked_flag():
    game_state = _build_state()
    spell = _basic_spell()
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    # Base cost {G} + kicker {1}{G} = total {1}{2G} = 3 mana needed
    player.mana_pool["G"] = 2
    player.mana_pool["C"] = 1
    graph = _spell_graph_with_keywords([
        {
            "id": "kw1",
            "type": "KEYWORD",
            "data": {"keyword": "kicker", "costs": [{"type": "mana", "cost": mana_cost_data("{1}{G}")}]},
        },
    ])

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={
            "choices": {
                "optional_costs": {"kicker:{1}{G}": 1},
                "optional_cost_payments": [
                    {"mana_payment": {"G": 1, "C": 1}},
                ],
            }
        },
    )

    stack_item = game_state.stack.items[-1]
    choices = (stack_item.payload.get("context") or {}).get("choices") or {}
    assert choices.get("kicked") is True
    assert choices.get("kicker_count") == 1


def test_buyback_returns_to_hand_on_resolution():
    game_state = _build_state()
    spell = _basic_spell()
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    # Base cost {G} + buyback {1}{G} = total {1}{2G} = 3 mana needed
    player.mana_pool["G"] = 2
    player.mana_pool["C"] = 1
    graph = _spell_graph_with_keywords([
        {
            "id": "kw1",
            "type": "KEYWORD",
            "data": {"keyword": "buyback", "costs": [{"type": "mana", "cost": mana_cost_data("{1}{G}")}]},
        },
    ])

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={
            "choices": {
                "optional_costs": {"buyback:{1}{G}": 1},
                "optional_cost_payments": [
                    {"mana_payment": {"G": 1, "C": 1}},
                ],
            }
        },
    )

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert spell.zone == ZONE_HAND


def test_kicked_condition_respects_choice():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    graph = {
        "rootNodeId": "act-1",
        "abilityType": "activated",
        "nodes": [
            {"id": "act-1", "type": "ACTIVATED", "data": {"cost": ""}},
            {"id": "c1", "type": "CONDITION", "data": {"type": "kicked"}},
            {"id": "e1", "type": "EFFECT", "data": {"type": "lose_life", "amount": 3, "target": "player"}},
        ],
        "edges": [
            {"from_": "act-1", "to": "c1"},
            {"from_": "c1", "to": "e1"},
        ],
    }
    adapter = AbilityGraphRuntimeAdapter(game_state)
    context = ResolveContext(controller_id=0, choices={"kicked": True}, targets={"target_player": 0})

    result = adapter.resolve(graph, context)

    assert result["status"] == "resolved"
    assert game_state.get_player(0).life == 17


def test_entwine_sets_all_modes_on_cast():
    game_state = _build_state()
    spell = _basic_spell()
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    # Base cost {G} + entwine {1}{G} = total {1}{2G} = 3 mana needed
    player.mana_pool["G"] = 2
    player.mana_pool["C"] = 1

    graph = {
        "rootNodeId": "act-1",
        "abilityType": "activated",
        "modal": {
            "min": 1,
            "max": 1,
            "modes": [{"id": "mode-a", "label": "Mode A"}, {"id": "mode-b", "label": "Mode B"}],
        },
        "nodes": [
            {"id": "act-1", "type": "ACTIVATED", "data": {"cost": ""}},
            {
                "id": "kw1",
                "type": "KEYWORD",
                "data": {"keyword": "entwine", "costs": [{"type": "mana", "cost": mana_cost_data("{1}{G}")}]},
            },
            {"id": "e1", "type": "EFFECT", "data": {"type": "lose_life", "amount": 1, "target": "player", "modeId": "mode-a"}},
            {"id": "e2", "type": "EFFECT", "data": {"type": "lose_life", "amount": 2, "target": "player", "modeId": "mode-b"}},
        ],
        "edges": [
            {"from_": "act-1", "to": "e1"},
            {"from_": "act-1", "to": "e2"},
        ],
    }

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={
            "choices": {
                "optional_costs": {"entwine:{1}{G}": 1},
                "optional_cost_payments": [
                    {"mana_payment": {"G": 1, "C": 1}},
                ],
            }
        },
    )

    stack_item = game_state.stack.items[-1]
    choices = (stack_item.payload.get("context") or {}).get("choices") or {}
    assert choices.get("entwine") is True
    assert set(choices.get("chosen_modes") or []) == {"mode-a", "mode-b"}


def test_entwine_allows_resolving_without_explicit_modes():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    graph = {
        "rootNodeId": "act-1",
        "abilityType": "activated",
        "modal": {
            "min": 1,
            "max": 1,
            "modes": [{"id": "mode-a", "label": "Mode A"}, {"id": "mode-b", "label": "Mode B"}],
        },
        "nodes": [
            {"id": "act-1", "type": "ACTIVATED", "data": {"cost": ""}},
            {"id": "e1", "type": "EFFECT", "data": {"type": "lose_life", "amount": 1, "target": "player", "modeId": "mode-a"}},
            {"id": "e2", "type": "EFFECT", "data": {"type": "lose_life", "amount": 2, "target": "player", "modeId": "mode-b"}},
        ],
        "edges": [
            {"from_": "act-1", "to": "e1"},
            {"from_": "act-1", "to": "e2"},
        ],
    }
    adapter = AbilityGraphRuntimeAdapter(game_state)
    context = ResolveContext(controller_id=0, choices={"entwine": True}, targets={"target_player": 0})

    result = adapter.resolve(graph, context)

    assert result["status"] == "resolved"
    assert game_state.get_player(0).life == 17


def test_replicate_creates_spell_copies():
    game_state = _build_state()
    spell = _basic_spell()
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    player.mana_pool["G"] = 3
    graph = _spell_graph_with_keywords([
        {
            "id": "kw1",
            "type": "KEYWORD",
            "data": {"keyword": "replicate", "costs": [{"type": "mana", "cost": mana_cost_data("{1}")}]},
        },
    ])

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={
            "choices": {
                "optional_costs": {"replicate:{1}": 2},
                "optional_cost_payments": [
                    {"mana_payment": {"G": 1}},
                    {"mana_payment": {"G": 1}},
                ],
            }
        },
    )

    assert len(game_state.stack.items) == 3
    copy_items = [item for item in game_state.stack.items if item.payload.get("is_copy")]
    assert len(copy_items) == 2


def test_kicker_non_mana_cost_sacrifice():
    game_state = _build_state()
    spell = _basic_spell()
    fodder = GameObject(
        id="fodder",
        name="Fodder",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(spell)
    game_state.add_object(fodder)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    player.mana_pool["G"] = 1
    graph = _spell_graph_with_keywords([
        {"id": "kw1", "type": "KEYWORD", "data": {"keyword": "kicker", "costs": [{"type": "sacrifice", "card_type": "Creature"}]}},
    ])

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=graph,
        context={
            "choices": {
                "optional_costs": {"kicker:sacrifice:Creature": 1},
                "optional_cost_payments": [
                    {"sacrifice_id": fodder.id},
                ],
            }
        },
    )

    assert fodder.zone == ZONE_GRAVEYARD

