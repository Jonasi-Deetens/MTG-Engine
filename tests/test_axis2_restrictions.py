from axis2.rules import restrictions as restriction_rules
from axis2.builder import Axis2Builder


# ------------------------------------------------------------
# ORACLE TEXT RESTRICTIONS
# ------------------------------------------------------------

def test_restriction_cast_only_during_your_turn(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Cast this spell only during your turn."

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cast_only_during_your_turn" in restrictions


def test_restriction_cast_only_during_opponents_turn(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Cast this spell only during an opponent's turn."

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cast_only_during_opponents_turn" in restrictions


def test_restriction_cast_only_during_combat(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Cast this spell only during combat."

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cast_only_during_combat" in restrictions


def test_restriction_cast_only_if_you_control_creature(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Cast this spell only if you control a creature."

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cast_only_if_you_control_creature" in restrictions


def test_restriction_cast_only_from_graveyard(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Cast this spell only from your graveyard."

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cast_only_from_graveyard" in restrictions


# ------------------------------------------------------------
# GLOBAL RESTRICTIONS
# ------------------------------------------------------------

def test_global_restriction_rule_of_law(hydra_axis1, game_state):
    game_state.global_restrictions.append({
        "applies_to": "all",
        "restriction": "one_spell_per_turn"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "limit_one_spell_per_turn" in restrictions


def test_global_restriction_silence(hydra_axis1, game_state):
    game_state.global_restrictions.append({
        "applies_to": "all",
        "restriction": "players_cannot_cast_spells"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cannot_cast_spells" in restrictions


def test_global_restriction_opponents_cannot_cast(hydra_axis1, game_state):
    game_state.global_restrictions.append({
        "applies_to": "opponents",
        "restriction": "opponents_cannot_cast_spells"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "opponents_cannot_cast_spells" in restrictions


def test_global_restriction_sorcery_speed(hydra_axis1, game_state):
    game_state.global_restrictions.append({
        "applies_to": "all",
        "restriction": "cast_only_sorcery_speed"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cast_only_sorcery_speed" in restrictions


# ------------------------------------------------------------
# CONTINUOUS EFFECT RESTRICTIONS
# ------------------------------------------------------------

def test_continuous_restriction_cannot_activate_abilities(hydra_axis1, game_state):
    game_state.continuous_effects.append({
        "type": "cannot_activate_abilities",
        "applies_to": "all"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cannot_activate_abilities" in restrictions


def test_continuous_restriction_cannot_cast_spells(hydra_axis1, game_state):
    game_state.continuous_effects.append({
        "type": "cannot_cast_spells",
        "applies_to": "all"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "cannot_cast_spells" in restrictions


def test_continuous_restriction_creature_cannot_attack(hydra_axis1, game_state):
    # Hydra is a creature → restriction applies
    game_state.continuous_effects.append({
        "type": "creatures_cannot_attack",
        "applies_to": "all"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "creature_cannot_attack" in restrictions


def test_continuous_restriction_creature_cannot_block(hydra_axis1, game_state):
    game_state.continuous_effects.append({
        "type": "creatures_cannot_block",
        "applies_to": "all"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    assert "creature_cannot_block" in restrictions


# ------------------------------------------------------------
# DEDUPLICATION
# ------------------------------------------------------------

def test_restrictions_deduplicate(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Cast this spell only during your turn."
    game_state.global_restrictions.append({
        "applies_to": "all",
        "restriction": "cast_only_sorcery_speed"
    })

    restrictions = restriction_rules.derive_restrictions(hydra_axis1, game_state).restrictions

    # Ensure no duplicates
    assert len(restrictions) == len(set(restrictions))


# ------------------------------------------------------------
# INTEGRATION WITH AXIS2 BUILDER
# ------------------------------------------------------------

def test_restrictions_integrate_with_axis2_builder(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Cast this spell only during your turn."

    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert "cast_only_during_your_turn" in cast_action.restrictions
