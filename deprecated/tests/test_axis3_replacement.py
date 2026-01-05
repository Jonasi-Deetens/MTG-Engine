from axis3.rules.actions import draw_card, cast_spell_from_hand, resolve_top_of_stack
from axis3.rules.sba import run_sbas
from axis3.state.zones import ZoneType as Zone

def test_enters_tapped(game_state_factory):
    # Card with Axis2 replacement: enters tapped
    game_state = game_state_factory(
        p0_cards=["Temple of Silence"],  # or any enters-tapped land
        p1_cards=[]
    )
    print(f"DEBUG game_state: {game_state}")
    draw_card(game_state, 0, 1)
    land_id = game_state.players[0].hand[0]

    cast_spell_from_hand(game_state, 0, land_id)
    resolve_top_of_stack(game_state)

    rt_obj = game_state.objects[land_id]
    assert rt_obj.tapped is True

def test_dies_exile_instead(game_state_factory):
    # Card with replacement effect: dies → exile instead
    game_state = game_state_factory(
        p0_cards=["Wurmcoil Engine"],  # imagine Axis2 gives it dies→exile replacement
        p1_cards=[]
    )

    # Draw the card
    draw_card(game_state, 0, 1)
    obj_id = game_state.players[0].hand[0]

    # Cast it
    cast_spell_from_hand(game_state, 0, obj_id)
    resolve_top_of_stack(game_state)

    rt_obj = game_state.objects[obj_id]

    # Simulate lethal damage
    rt_obj.damage = rt_obj.characteristics.toughness

    # Run SBAs (this triggers the zone_change event)
    run_sbas(game_state)

    # Replacement effect should have changed the destination to EXILE
    assert rt_obj.zone == Zone.EXILE
