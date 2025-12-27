from axis3.engine.controller import PlayerController, PlayerAction, PlayerActionType
from axis3.state.zones import ZoneType as Zone
from axis3.engine.engine import run_full_turn
from axis3.rules.actions import draw_card


class SingleCastCreatureController(PlayerController):
    def __init__(self):
        self.has_cast = False

    def choose_action(self, game_state, player_id):
        ps = game_state.players[player_id]
        if not self.has_cast and ps.hand:
            obj_id = ps.hand[0]
            self.has_cast = True
            return PlayerAction(
                type=PlayerActionType.CAST_SPELL_FROM_HAND,
                obj_id=obj_id,
            )
        return PlayerAction(type=PlayerActionType.PASS_PRIORITY)


def test_full_turn_cast_creature(game_state_factory):
    # Build game where P0 has a vanilla creature on top of library
    game_state = game_state_factory(
        p0_cards=["Grizzly Bears"],  # any simple creature
        p1_cards=[]
    )

    # P0 draws their creature
    draw_card(game_state, 0, 1)

    controllers = {
        0: SingleCastCreatureController(),
        1: SingleCastCreatureController(),  # unused for now
    }

    # Run one full turn
    run_full_turn(game_state, controllers)

    p0 = game_state.players[0]
    assert len(p0.battlefield) == 1
    obj_id = p0.battlefield[0]
    rt_obj = game_state.objects[obj_id]

    assert rt_obj.zone == Zone.BATTLEFIELD
    assert "Creature" in rt_obj.characteristics.types
    assert rt_obj.summoning_sick is True
