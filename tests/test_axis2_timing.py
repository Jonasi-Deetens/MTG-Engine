from axis2.builder import Axis2Builder


def test_creature_default_timing_is_sorcery(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert cast_action.timing.speed == "sorcery"
    assert cast_action.timing.requires_priority is True
    assert cast_action.timing.stack_must_be_empty is True
    assert "main" in cast_action.timing.phases


def test_instant_default_timing_is_instant(hydra_axis1, game_state):
    # Modify Hydra to behave like an instant
    hydra_axis1.characteristics.card_types = ["Instant"]

    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert cast_action.timing.speed == "instant"
    assert cast_action.timing.stack_must_be_empty is False
    assert cast_action.timing.requires_priority is True
    assert cast_action.timing.phases == []


def test_flash_keyword_grants_instant_speed(hydra_axis1, game_state):
    hydra_axis1.faces[0].keywords.append("Flash")

    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert cast_action.timing.speed == "instant"
