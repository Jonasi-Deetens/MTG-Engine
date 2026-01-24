import pytest

from engine import GameObject, GameState, PlayerState, TurnManager
from engine.rules import activate_ability
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def _activation_graph(costs: list[dict]) -> dict:
    return {
        "id": "graph-1",
        "sourceKind": "permanent",
        "steps": [
            {
                "id": "step-1",
                "effect": {
                    "id": "eff-1",
                    "initiation": "activated",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "cost": {"items": costs},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "life", "amount": 0},
                    },
                },
            },
        ],
    }


def test_activate_tap_cost_taps_source():
    game_state = _build_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_activation_graph([{"type": "tap_self"}])],
    )
    source.keywords.add("Haste")
    game_state.add_object(source)
    turn_manager = TurnManager(game_state)

    activate_ability(game_state, turn_manager, player_id=0, object_id=source.id)

    assert source.tapped is True
    assert game_state.stack.items


def test_activate_sacrifice_cost():
    game_state = _build_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_activation_graph([{"type": "sacrifice", "card_type": "Creature"}])],
    )
    sacrifice = GameObject(
        id="fodder",
        name="Fodder",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(source)
    game_state.add_object(sacrifice)
    turn_manager = TurnManager(game_state)

    activate_ability(
        game_state,
        turn_manager,
        player_id=0,
        object_id=source.id,
        context={"choices": {"cost_payments": {source.id: {"sacrifice_id": sacrifice.id}}}},
    )

    assert sacrifice.zone == ZONE_GRAVEYARD


def test_activate_discard_cost():
    game_state = _build_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_activation_graph([{"type": "discard", "amount": 2}])],
    )
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
    game_state.add_object(source)
    game_state.add_object(card_a)
    game_state.add_object(card_b)
    turn_manager = TurnManager(game_state)

    activate_ability(
        game_state,
        turn_manager,
        player_id=0,
        object_id=source.id,
        context={"choices": {"cost_payments": {source.id: {"discard_ids": [card_a.id, card_b.id]}}}},
    )

    assert card_a.zone == ZONE_GRAVEYARD
    assert card_b.zone == ZONE_GRAVEYARD


def test_activate_tap_choice_cost():
    game_state = _build_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_activation_graph([{"type": "tap", "card_type": "Creature"}])],
    )
    tap_target = GameObject(
        id="tap_target",
        name="Tap Target",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(source)
    game_state.add_object(tap_target)
    turn_manager = TurnManager(game_state)

    activate_ability(
        game_state,
        turn_manager,
        player_id=0,
        object_id=source.id,
        context={"choices": {"cost_payments": {source.id: {"tap_id": tap_target.id}}}},
    )

    assert tap_target.tapped is True


def test_activate_pay_life_cost():
    game_state = _build_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        effect_graphs=[_activation_graph([{"type": "life", "amount": 3}])],
    )
    game_state.add_object(source)
    turn_manager = TurnManager(game_state)
    starting_life = game_state.get_player(0).life

    activate_ability(game_state, turn_manager, player_id=0, object_id=source.id)

    assert game_state.get_player(0).life == starting_life - 3

