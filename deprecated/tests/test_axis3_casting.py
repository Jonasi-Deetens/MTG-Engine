from axis3.rules.actions import draw_card, cast_spell_from_hand
from axis3.state.zones import ZoneType as Zone
from axis3.rules.actions import resolve_top_of_stack

def test_cast_creature_enters_battlefield(game_state_factory):
    # game_state_factory should build a game with 2 players and 1 creature in hand for P0

    game_state = game_state_factory(
        p0_cards=["Grizzly Bears"],  # or any 2/2 creature
        p1_cards=[]
    )

    p0 = game_state.players[0]

    # Draw the creature
    draw_card(game_state, 0, 1)

    assert len(p0.hand) == 1

    obj_id = p0.hand[0]

    # Cast it
    cast_spell_from_hand(game_state, 0, obj_id)
    print("Stack after casting:", [item for item in game_state.stack.items])

    resolve_top_of_stack(game_state)
    # Should now be on battlefield
    assert obj_id in p0.battlefield

    rt_obj = game_state.objects[obj_id]
    assert rt_obj.zone == Zone.BATTLEFIELD
    assert rt_obj.summoning_sick is True
