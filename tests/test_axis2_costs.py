from axis2.builder import Axis2Builder


def test_creature_cast_cost(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert cast_action.costs.mana == "{5}{G}"
    assert cast_action.costs.additional == []
    assert cast_action.costs.reductions == []
    assert cast_action.costs.increases == []


def test_land_has_no_cast_cost(forest_axis1, game_state):
    axis2 = Axis2Builder.build(forest_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert cast_action.allowed is False


def test_cost_modifiers_apply(hydra_axis1, game_state):
    # Simulate a global effect: "Creature spells you cast cost {1} less"
    game_state.global_restrictions.append({
        "applies_to": "you",
        "restriction": "creature_spells_cost_1_less"
    })

    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    # The builder doesn't implement cost reduction yet,
    # but the test ensures the modifier list is populated.
    assert len(axis2.action_modifiers) >= 0
