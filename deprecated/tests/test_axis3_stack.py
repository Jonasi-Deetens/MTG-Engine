from axis3.rules.actions import draw_card, cast_spell_from_hand, resolve_top_of_stack
from axis3.state.zones import ZoneType as Zone

def test_stack_lifo_resolution(game_state_factory):
    # Build a game with two sorceries in hand
    game_state = game_state_factory(
        p0_cards=["Shock", "Opt"],
        p1_cards=[]
    )

    # Draw both spells
    draw_card(game_state, 0, 2)
    p0 = game_state.players[0]

    spell1 = p0.hand[0]
    spell2 = p0.hand[1]

    # Cast both
    cast_spell_from_hand(game_state, 0, spell1)
    cast_spell_from_hand(game_state, 0, spell2)

    # Top of stack should be spell2
    assert game_state.stack.items[-1].obj_id == spell2

    # Resolve top
    resolve_top_of_stack(game_state)
    assert game_state.objects[spell2].zone == Zone.GRAVEYARD

    # Resolve next
    resolve_top_of_stack(game_state)
    assert game_state.objects[spell1].zone == Zone.GRAVEYARD

    # Stack empty
    assert game_state.stack.is_empty()
