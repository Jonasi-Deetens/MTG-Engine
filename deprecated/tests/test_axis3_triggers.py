from axis3.rules.actions import draw_card, cast_spell_from_hand, resolve_top_of_stack

def test_etb_trigger_draw_card(game_state_factory):
    game_state = game_state_factory(
        p0_cards=["Elvish Visionary"], 
        p0_library=["Fog of Gnats"],
        p1_cards=[]
    )

    print(f"DEBUG hand 1: {game_state.players[0].hand}")

    draw_card(game_state, 0, 1)
    card_id = game_state.players[0].hand[0]
    assert game_state.objects[card_id].axis1.faces[0].name == "Elvish Visionary"

    print(f"DEBUG hand 2: {game_state.players[0].hand}")

    # Cast it
    cast_spell_from_hand(game_state, 0, card_id)
    resolve_top_of_stack(game_state)
    print(f"DEBUG stack: {game_state.stack.items}")

    print(f"DEBUG hand 3: {game_state.players[0].hand}")

    assert len(game_state.stack.items) == 1

    resolve_top_of_stack(game_state)

    assert len(game_state.players[0].hand) == 1
    new_card_id = game_state.players[0].hand[0]
    print(f"DEBUG player library: {game_state.players[0].library}")
    new_card_name = game_state.objects[new_card_id].axis1.faces[0].name
    assert new_card_name == "Fog of Gnats"