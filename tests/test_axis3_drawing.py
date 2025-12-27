from axis3.rules.actions import draw_card
from axis3.translate.loader import build_game_state_from_decks

def test_initial_draws(axis1_deck_p1, axis1_deck_p2, axis2_builder):
    game_state = build_game_state_from_decks(axis1_deck_p1, axis1_deck_p2, axis2_builder)

    assert len(game_state.players[0].library) == len(axis1_deck_p1)
    assert len(game_state.players[0].hand) == 0

    draw_card(game_state, player_id=0, n=7)

    assert len(game_state.players[0].hand) == 7
    assert len(game_state.players[0].library) == len(axis1_deck_p1) - 7

    # No duplicates, all object ids are unique
    all_ids = list(game_state.objects.keys())
    assert len(all_ids) == len(set(all_ids))
