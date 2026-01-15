import pytest

from engine import GameObject, GameState, PlayerState, TurnManager
from engine.rules import (
    assign_combat_damage,
    cast_spell,
    declare_attackers,
    declare_blockers,
    play_land,
)
from engine.turn import Phase, Step
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND


def _build_game_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def test_play_land_once_per_turn():
    game_state = _build_game_state()
    land = GameObject(
        id="land_1",
        name="Forest",
        owner_id=0,
        controller_id=0,
        types=["Land"],
        zone=ZONE_HAND,
    )
    game_state.add_object(land)

    turn_manager = TurnManager(game_state)
    play_land(game_state, turn_manager, player_id=0, object_id=land.id)

    assert land.zone == ZONE_BATTLEFIELD
    assert land.id in game_state.get_player(0).battlefield
    assert game_state.turn.land_plays_this_turn == 1

    with pytest.raises(ValueError):
        play_land(game_state, turn_manager, player_id=0, object_id=land.id)


def test_cast_non_instant_requires_main_phase():
    game_state = _build_game_state()
    creature = GameObject(
        id="creature_1",
        name="Test Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_HAND,
        power=2,
        toughness=2,
    )
    game_state.add_object(creature)

    turn_manager = TurnManager(game_state)
    cast_spell(game_state, turn_manager, player_id=0, object_id=creature.id)

    assert len(game_state.stack.items) == 1
    assert game_state.stack.items[0].payload["object_id"] == creature.id
    assert game_state.stack.items[0].payload["destination_zone"] == ZONE_BATTLEFIELD

    game_state.turn.step = Step.DRAW
    game_state.turn.phase = Phase.BEGINNING
    with pytest.raises(ValueError):
        cast_spell(game_state, turn_manager, player_id=0, object_id=creature.id)


def test_declare_attackers_and_blockers():
    game_state = _build_game_state()
    attacker = GameObject(
        id="attacker_1",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    blocker = GameObject(
        id="blocker_1",
        name="Blocker",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    game_state.add_object(attacker)
    game_state.add_object(blocker)

    game_state.turn.step = Step.DECLARE_ATTACKERS
    game_state.turn.phase = Phase.COMBAT
    game_state.turn.priority_current_index = 0
    turn_manager = TurnManager(game_state)
    declare_attackers(game_state, turn_manager, player_id=0, attackers=[attacker.id], defending_player_id=1)

    assert attacker.is_attacking is True
    assert attacker.tapped is True
    assert game_state.turn.combat_state is not None

    game_state.turn.step = Step.DECLARE_BLOCKERS
    game_state.turn.priority_current_index = 1
    turn_manager = TurnManager(game_state)
    declare_blockers(game_state, turn_manager, player_id=1, blockers={attacker.id: [blocker.id]})

    assert blocker.is_blocking is True
    assert game_state.turn.combat_state.blockers[attacker.id] == [blocker.id]


def test_assign_combat_damage_to_player():
    game_state = _build_game_state()
    attacker = GameObject(
        id="attacker_2",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=4,
        toughness=4,
    )
    game_state.add_object(attacker)

    game_state.turn.step = Step.DECLARE_ATTACKERS
    game_state.turn.phase = Phase.COMBAT
    game_state.turn.priority_current_index = 0
    turn_manager = TurnManager(game_state)
    declare_attackers(game_state, turn_manager, player_id=0, attackers=[attacker.id], defending_player_id=1)

    game_state.turn.step = Step.COMBAT_DAMAGE
    game_state.turn.priority_current_index = 0
    turn_manager = TurnManager(game_state)
    assign_combat_damage(game_state, turn_manager, player_id=0)

    assert game_state.get_player(1).life == 36

