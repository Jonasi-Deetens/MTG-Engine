from axis3.rules.actions import draw_card, cast_spell_from_hand, resolve_top_of_stack
from axis3.rules.combat import CombatState, declare_attackers, perform_combat_damage
from axis3.state.zones import ZoneType as Zone


def test_simple_attack_for_two(game_state_factory):
    """
    P0 casts a 2/2 creature, next turn attacks, P1 loses 2 life.
    """

    # game_state_factory should:
    # - build a game where P0's top library card is a 2/2 creature (e.g. Grizzly Bears)
    # - P1 has an empty deck or irrelevant cards
    game_state = game_state_factory(
        p0_cards=["Grizzly Bears"],
        p1_cards=[]
    )

    p0 = game_state.players[0]
    p1 = game_state.players[1]

    # P0 draws and casts the creature
    draw_card(game_state, 0, 1)
    assert len(p0.hand) == 1
    creature_id = p0.hand[0]

    cast_spell_from_hand(game_state, 0, creature_id)
    # spell is on stack
    assert not game_state.stack.is_empty()

    resolve_top_of_stack(game_state)
    # now on battlefield
    assert creature_id in p0.battlefield
    rt_obj = game_state.objects[creature_id]
    assert rt_obj.zone == Zone.BATTLEFIELD
    assert rt_obj.summoning_sick is True

    # Simulate passing a turn so summoning sickness wears off.
    # Simplest: manually clear summoning_sick and untap.
    rt_obj.summoning_sick = False
    rt_obj.tapped = False

    # Begin combat: declare attackers
    combat_state = CombatState()
    declare_attackers(
        game_state,
        combat_state,
        attacking_player_id=0,
        attacker_ids=[creature_id],
        defending_player_id=1,
    )

    assert rt_obj.tapped is True
    assert combat_state.attackers[creature_id] == 1

    # Combat damage
    starting_life_p1 = p1.life
    perform_combat_damage(game_state, combat_state)

    assert p1.life == starting_life_p1 - 2  # Grizzly Bears is 2/2
