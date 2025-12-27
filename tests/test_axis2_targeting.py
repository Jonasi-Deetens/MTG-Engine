from axis2.builder import Axis2Builder


def test_default_creature_has_no_targeting(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert cast_action.targeting_rules.required is False
    assert cast_action.targeting_rules.legal_targets == []
    assert cast_action.targeting_rules.min == 0
    assert cast_action.targeting_rules.max == 0


def test_targeting_restrictions_structure(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    targeting = axis2.actions["cast_spell"].targeting_rules

    assert isinstance(targeting.restrictions, list)
    assert isinstance(targeting.replacement_effects, list)


def test_targeting_replacement_effects(hydra_axis1, game_state):
    # Simulate ward or hexproof
    game_state.replacement_effects.append("ward")

    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    targeting = axis2.actions["cast_spell"].targeting_rules

    assert isinstance(targeting.replacement_effects, list)
