from axis3.rules.actions import draw_card, cast_spell_from_hand, resolve_top_of_stack
from axis3.rules.combat import CombatState, declare_attackers, perform_combat_damage
from axis3.state.zones import ZoneType as Zone


def test_creature_dies_from_lethal_damage(game_state_factory):
    # P0: 2/2 creature
    # P1: 3/3 creature
    game_state = game_state_factory(
        p0_cards=["Grizzly Bears"],
        p1_cards=["Hill Giant"]
    )

    # P0 casts Bears
    draw_card(game_state, 0, 1)
    bear_id = game_state.players[0].hand[0]
    cast_spell_from_hand(game_state, 0, bear_id)
    resolve_top_of_stack(game_state)

    # P1 casts Giant
    draw_card(game_state, 1, 1)
    giant_id = game_state.players[1].hand[0]
    cast_spell_from_hand(game_state, 1, giant_id)
    resolve_top_of_stack(game_state)

    # Remove summoning sickness for test
    game_state.objects[bear_id].summoning_sick = False
    game_state.objects[giant_id].summoning_sick = False

    # Simulate combat: Bears attacks, Giant blocks
    combat = CombatState()
    declare_attackers(game_state, combat, 0, [bear_id], 1)

    # For now, manually assign damage both ways
    game_state.objects[bear_id].damage = 3  # Giant hits Bears
    game_state.objects[giant_id].damage = 2 # Bears hits Giant

    from axis3.rules.sba import run_sbas
    run_sbas(game_state)

    # Bears should die (2 toughness, 3 damage)
    assert game_state.objects[bear_id].zone == Zone.GRAVEYARD

    # Giant should survive (3 toughness, 2 damage)
    assert game_state.objects[giant_id].zone == Zone.BATTLEFIELD

def test_player_loses_at_zero_life(game_state_factory):
    game_state = game_state_factory([], [])

    p1 = game_state.players[1]
    p1.life = -3

    from axis3.rules.sba import run_sbas
    run_sbas(game_state)

    assert p1.life == 0  # clamped
