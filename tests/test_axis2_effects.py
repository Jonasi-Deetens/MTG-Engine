from axis2.rules import effects as effects_rules
from axis2.builder import Axis2Builder


# ------------------------------------------------------------
# TRIGGER TESTS
# ------------------------------------------------------------

def test_etb_trigger(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "When CARDNAME enters the battlefield, draw a card."

    triggers = effects_rules.derive_triggers(hydra_axis1, game_state)

    assert any(t.event == "enters_battlefield" for t in triggers)


def test_ltb_trigger(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "When CARDNAME dies, draw a card."

    triggers = effects_rules.derive_triggers(hydra_axis1, game_state)

    assert any(t.event == "dies" for t in triggers)


def test_attack_trigger(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Whenever CARDNAME attacks, it gets +1/+1."

    triggers = effects_rules.derive_triggers(hydra_axis1, game_state)

    assert any(t.event == "attacks" for t in triggers)


def test_block_trigger(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Whenever CARDNAME blocks, it gets +1/+1."

    triggers = effects_rules.derive_triggers(hydra_axis1, game_state)

    assert any(t.event == "blocks" for t in triggers)


def test_upkeep_trigger(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "At the beginning of your upkeep, draw a card."

    triggers = effects_rules.derive_triggers(hydra_axis1, game_state)

    assert any(t.event == "upkeep" for t in triggers)


def test_draw_step_trigger(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "At the beginning of your draw step, scry 1."

    triggers = effects_rules.derive_triggers(hydra_axis1, game_state)

    assert any(t.event == "draw_step" for t in triggers)


def test_end_step_trigger(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "At the beginning of your end step, gain 1 life."

    triggers = effects_rules.derive_triggers(hydra_axis1, game_state)

    assert any(t.event == "end_step" for t in triggers)


# ------------------------------------------------------------
# REPLACEMENT EFFECT TESTS
# ------------------------------------------------------------

def test_replacement_effect_dies_exile(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "If CARDNAME would die, exile it instead."

    effects = effects_rules.derive_replacement_effects(hydra_axis1, game_state)

    assert "dies_exile_instead" in effects


def test_replacement_effect_enter_tapped(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "CARDNAME enters the battlefield tapped."

    effects = effects_rules.derive_replacement_effects(hydra_axis1, game_state)

    assert "enter_tapped" in effects


def test_replacement_effect_draw_replacement(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "If you would draw a card, draw two instead."

    effects = effects_rules.derive_replacement_effects(hydra_axis1, game_state)

    assert "draw_replacement" in effects


def test_replacement_effect_damage_replacement(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "If CARDNAME would deal damage, prevent that damage."

    effects = effects_rules.derive_replacement_effects(hydra_axis1, game_state)

    assert "damage_replacement" in effects


def test_replacement_effects_include_game_state(hydra_axis1, game_state):
    game_state.replacement_effects.append("ward")

    effects = effects_rules.derive_replacement_effects(hydra_axis1, game_state)

    assert "ward" in effects


# ------------------------------------------------------------
# STATIC EFFECT TESTS
# ------------------------------------------------------------

def test_static_effect_buff_creatures(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Creatures you control get +1/+1."

    effects = effects_rules.derive_static_effects(hydra_axis1, game_state)

    assert any(key.startswith("pt_modifier_creatures_you_control") for key in effects)    

def test_static_effect_opponent_spells_cost_more(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Spells your opponents cast cost {1} more."

    effects = effects_rules.derive_static_effects(hydra_axis1, game_state)

    assert any(key.startswith("opponent_spells_cost_more") for key in effects)


def test_static_effect_opponents_cannot_gain_life(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Your opponents can't gain life."

    effects = effects_rules.derive_static_effects(hydra_axis1, game_state)

    assert any(key.startswith("opponents_cannot_gain_life") for key in effects)


def test_static_effects_include_game_state(hydra_axis1, game_state):
    game_state.continuous_effects.append({"type": "creatures_cannot_attack"})

    effects = effects_rules.derive_static_effects(hydra_axis1, game_state)

    assert any(key.startswith("creatures_cannot_attack") for key in effects)


# ------------------------------------------------------------
# DEDUPLICATION
# ------------------------------------------------------------

def test_effects_deduplicate(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "If CARDNAME would die, exile it instead."
    game_state.replacement_effects.append("dies_exile_instead")

    effects = effects_rules.derive_replacement_effects(hydra_axis1, game_state)

    assert effects.count("dies_exile_instead") == 1


# ------------------------------------------------------------
# INTEGRATION WITH AXIS2 BUILDER
# ------------------------------------------------------------

def test_effects_integrate_with_axis2_builder(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "When CARDNAME enters the battlefield, draw a card."

    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    assert any(t.event == "enters_battlefield" for t in axis2.triggers)
