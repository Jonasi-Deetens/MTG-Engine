from engine import GameState, GameObject, PlayerState
from engine.commander import apply_commander_tax, record_commander_damage, register_commander
from engine.damage import apply_damage_to_player
from engine.sba import apply_state_based_actions
from engine.zones import ZONE_COMMAND


def test_commander_tax_and_damage_tracking():
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)

    commander = GameObject(
        id="commander_1",
        name="Commander",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_COMMAND,
    )
    game_state.add_object(commander)
    register_commander(game_state, 0, commander.id)

    assert players[0].commander_id == commander.id
    assert commander.id in players[0].command

    assert apply_commander_tax(game_state, 0) == 0
    assert players[0].commander_tax == 2
    assert apply_commander_tax(game_state, 0) == 2
    assert players[0].commander_tax == 4

    record_commander_damage(game_state, commander.id, 1, 5)
    record_commander_damage(game_state, commander.id, 1, 3)
    assert players[1].commander_damage_taken[commander.id] == 8


def test_commander_damage_causes_loss():
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    commander = GameObject(
        id="commander_2",
        name="Commander",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_COMMAND,
    )
    game_state.add_object(commander)
    register_commander(game_state, 0, commander.id)

    apply_damage_to_player(game_state, commander, player_id=1, amount=21)
    apply_state_based_actions(game_state)

    assert players[1].has_lost is True
    assert players[1].removed_from_game is True
