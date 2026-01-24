from engine import GameObject, GameState, PlayerState, TurnManager, Phase, Step
from engine.rules import cast_spell
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    return game_state


def test_ward_requires_payment_choice():
    game_state = _build_state()
    warded = GameObject(
        id="warded",
        name="Warded",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(warded)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        context={"targets": {"target": warded.id, "targets": [warded.id]}, "choices": {}},
    )
    assert game_state.stack.items


def test_ward_payment_allows_targeting():
    game_state = _build_state()
    warded = GameObject(
        id="warded",
        name="Warded",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(warded)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        context={
            "targets": {"target": warded.id, "targets": [warded.id]},
            "choices": {"ward_auto_pay": True},
        },
    )

    assert game_state.stack.items


def test_ward_payment_uses_specific_mana_payment():
    game_state = _build_state()
    warded = GameObject(
        id="warded",
        name="Warded",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(warded)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        context={
            "targets": {"target": warded.id, "targets": [warded.id]},
            "choices": {"ward_payments": {warded.id: {"mana_payment": {"C": 1}}}},
        },
    )

    assert game_state.get_player(0).mana_pool.get("C", 0) == 0

