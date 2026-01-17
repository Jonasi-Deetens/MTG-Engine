import pytest

from engine import GameObject, GameState, PlayerState, TurnManager
from engine.rules import (
    assign_combat_damage,
    cast_spell,
    declare_attackers,
    declare_blockers,
    play_land,
)
from engine.stack import StackItem
from engine.turn import Phase, Step
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND, ZONE_LIBRARY


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


def test_declare_attackers_allows_empty():
    game_state = _build_game_state()
    game_state.turn.step = Step.DECLARE_ATTACKERS
    game_state.turn.phase = Phase.COMBAT
    game_state.turn.priority_current_index = 0
    turn_manager = TurnManager(game_state)

    declare_attackers(game_state, turn_manager, player_id=0, attackers=[], defending_player_id=1)

    assert game_state.turn.combat_state is not None
    assert game_state.turn.combat_state.attackers == []
    assert game_state.turn.combat_state.attackers_declared is True


def test_declare_blockers_allows_empty():
    game_state = _build_game_state()
    attacker = GameObject(
        id="attacker_empty_block",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    game_state.add_object(attacker)

    game_state.turn.step = Step.DECLARE_ATTACKERS
    game_state.turn.phase = Phase.COMBAT
    game_state.turn.priority_current_index = 0
    turn_manager = TurnManager(game_state)
    declare_attackers(game_state, turn_manager, player_id=0, attackers=[attacker.id], defending_player_id=1)

    game_state.turn.step = Step.DECLARE_BLOCKERS
    game_state.turn.priority_current_index = 1
    turn_manager = TurnManager(game_state)
    declare_blockers(game_state, turn_manager, player_id=1, blockers={})

    assert game_state.turn.combat_state.blockers_declared is True
    assert game_state.turn.combat_state.blockers == {}


def test_copy_spell_resolves_without_moving_source():
    game_state = _build_game_state()
    spell = GameObject(
        id="spell_copy",
        name="Lightning Bolt",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone="stack",
    )
    game_state.add_object(spell)
    game_state.stack.push(
        StackItem(kind="spell", payload={"object_id": spell.id, "destination_zone": "graveyard"}, controller_id=0)
    )
    game_state.stack.push(
        StackItem(kind="spell", payload={"copy_of": spell.id, "is_copy": True, "context": {}}, controller_id=0)
    )

    turn_manager = TurnManager(game_state)
    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert spell.zone == "stack"
    assert game_state.stack.items[-1].payload.get("object_id") == spell.id


def test_draw_step_skips_first_turn_for_starting_player():
    game_state = _build_game_state()
    game_state.turn.turn_number = 1
    game_state.turn.active_player_index = 0
    card = GameObject(
        id="draw_skip",
        name="Draw Skip",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_LIBRARY,
    )
    game_state.add_object(card)

    turn_manager = TurnManager(game_state)
    turn_manager._handle_draw_step()

    assert card.id in game_state.get_player(0).library
    assert card.id not in game_state.get_player(0).hand


def test_draw_step_draws_after_first_turn():
    game_state = _build_game_state()
    game_state.turn.turn_number = 2
    game_state.turn.active_player_index = 0
    card = GameObject(
        id="draw_normal",
        name="Draw Normal",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_LIBRARY,
    )
    game_state.add_object(card)

    turn_manager = TurnManager(game_state)
    turn_manager._handle_draw_step()

    assert card.id in game_state.get_player(0).hand


def test_cleanup_discards_to_hand_size():
    game_state = _build_game_state()
    player = game_state.get_player(0)
    player.max_hand_size = 7
    for idx in range(9):
        card = GameObject(
            id=f"hand_{idx}",
            name=f"Card {idx}",
            owner_id=0,
            controller_id=0,
            types=["Instant"],
            zone=ZONE_HAND,
        )
        game_state.add_object(card)

    turn_manager = TurnManager(game_state)
    turn_manager._handle_cleanup_step()

    assert len(player.hand) == 7
    assert len(player.graveyard) == 2


def test_priority_skips_players_who_lost():
    players = [PlayerState(id=0), PlayerState(id=1), PlayerState(id=2)]
    players[1].has_lost = True
    game_state = GameState(players=players)
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    game_state.turn.active_player_index = 1
    game_state.turn.priority_current_index = 0

    turn_manager = TurnManager(game_state)

    assert turn_manager.current_active_player_id() != 1
    assert 1 not in turn_manager.priority.player_order

    turn_manager.handle_player_pass(turn_manager.priority.current)
    assert turn_manager.priority.current == 2


def test_combat_damage_can_target_planeswalker():
    game_state = _build_game_state()
    attacker = GameObject(
        id="pw_attacker",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=4,
        toughness=4,
    )
    planeswalker = GameObject(
        id="pw_defender",
        name="Planeswalker",
        owner_id=1,
        controller_id=1,
        types=["Planeswalker"],
        zone=ZONE_BATTLEFIELD,
    )
    planeswalker.counters["loyalty"] = 6
    game_state.add_object(attacker)
    game_state.add_object(planeswalker)

    game_state.turn.step = Step.DECLARE_ATTACKERS
    game_state.turn.phase = Phase.COMBAT
    game_state.turn.priority_current_index = 0
    turn_manager = TurnManager(game_state)
    declare_attackers(
        game_state,
        turn_manager,
        player_id=0,
        attackers=[attacker.id],
        defending_player_id=1,
        defending_object_id=planeswalker.id,
    )

    game_state.turn.step = Step.COMBAT_DAMAGE
    game_state.turn.priority_current_index = 0
    turn_manager = TurnManager(game_state)
    assign_combat_damage(game_state, turn_manager, player_id=0)

    assert planeswalker.counters.get("loyalty") == 2
    assert game_state.get_player(1).life == 40


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

