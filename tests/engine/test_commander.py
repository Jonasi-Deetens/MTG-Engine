from engine import GameState, GameObject, PlayerState
from engine.commander import apply_commander_tax, record_commander_damage, register_commander
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
