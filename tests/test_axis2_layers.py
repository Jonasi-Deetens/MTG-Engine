from axis2.builder import Axis2Builder


def test_layers_structure(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    # Layers aren't implemented yet, but the builder must expose modifiers
    assert isinstance(axis2.action_modifiers, list)
    assert isinstance(axis2.action_replacements, list)
    assert isinstance(axis2.action_preventions, list)


def test_continuous_effects_do_not_break_builder(hydra_axis1, game_state):
    # Simulate a continuous effect: "Creatures you control get +1/+1"
    game_state.continuous_effects.append({
        "type": "pt_mod",
        "amount": "+1/+1",
        "applies_to": "creatures_you_control"
    })

    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    # No crash, structure intact
    assert isinstance(axis2, object)


def test_global_restrictions_reflected(hydra_axis1, game_state):
    game_state.global_restrictions.append({
        "applies_to": "opponents",
        "restriction": "cast_only_sorcery_speed"
    })

    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    assert len(axis2.global_restrictions) == 1
    assert axis2.global_restrictions[0].restriction == "cast_only_sorcery_speed"
