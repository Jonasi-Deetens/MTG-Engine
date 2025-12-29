from axis3.rules.actions import draw_card, cast_spell_from_hand, resolve_top_of_stack
from axis3.rules.layers import evaluate_characteristics
from axis3.state.zones import ZoneType as Zone


def test_global_anthem_buff(game_state_factory):
    # Suppose "Glorious Anthem": "Creatures you control get +1/+1"
    game_state = game_state_factory(
        p0_cards=["Grizzly Bears", "Glorious Anthem"],
        p1_cards=[]
    )

    # Draw both
    draw_card(game_state, 0, 2)
    hand = game_state.players[0].hand
    bear_id = hand[0]
    anthem_id = hand[1]

    # Cast Bears
    cast_spell_from_hand(game_state, 0, bear_id)
    resolve_top_of_stack(game_state)

    # Cast Anthem
    cast_spell_from_hand(game_state, 0, anthem_id)
    resolve_top_of_stack(game_state)

    # Build continuous effects for Anthem (you'll hook this in automatically
    # on ETB later, but for now you can call the builder explicitly)
    from axis3.compiler.continuous_builder import build_continuous_effects_for_object
    build_continuous_effects_for_object(game_state, game_state.objects[anthem_id])

    ec = evaluate_characteristics(game_state, bear_id)
    # Base Bears is 2/2, Anthem makes it 3/3
    assert ec.power == 3
    assert ec.toughness == 3

def test_aura_buff_and_ability(game_state_factory):
    # Imagine "Holy Strength Aura": "Enchanted creature gets +2/+2 and has flying"
    game_state = game_state_factory(
        p0_cards=["Grizzly Bears", "Holy Strength Aura"],
        p1_cards=[]
    )

    from axis3.rules.actions import draw_card, cast_spell_from_hand, resolve_top_of_stack
    from axis3.rules.layers import evaluate_characteristics

    draw_card(game_state, 0, 2)
    bear_id, aura_id = game_state.players[0].hand

    # Cast Bears
    cast_spell_from_hand(game_state, 0, bear_id)
    resolve_top_of_stack(game_state)

    # Cast Aura (skip targeting correctness; just attach it)
    cast_spell_from_hand(game_state, 0, aura_id)
    resolve_top_of_stack(game_state)

    # Manually attach aura for test
    aura = game_state.objects[aura_id]
    aura.attached_to = bear_id

    from axis3.compiler.continuous_builder import build_continuous_effects_for_object
    build_continuous_effects_for_object(game_state, aura)

    ec = evaluate_characteristics(game_state, bear_id)
    assert ec.power == 4  # 2 + 2
    assert ec.toughness == 4
    assert "flying" in ec.abilities
