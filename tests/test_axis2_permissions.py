from axis2.rules import permissions as permission_rules
from axis2.builder import Axis2Builder


# ------------------------------------------------------------
# ORACLE TEXT PERMISSIONS
# ------------------------------------------------------------

def test_permission_cast_from_graveyard_oracle(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "You may cast this card from your graveyard."

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "may_cast_from_graveyard" in perms


def test_permission_cast_from_exile_oracle(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "You may cast this card from exile."

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "may_cast_from_exile" in perms


def test_permission_play_lands_from_graveyard_oracle(forest_axis1, game_state):
    forest_axis1.faces[0].oracle_text = "You may play lands from your graveyard."

    perms = permission_rules.derive_permissions(forest_axis1, game_state).permissions

    assert "may_play_lands_from_graveyard" in perms


def test_permission_additional_land_play_oracle(forest_axis1, game_state):
    forest_axis1.faces[0].oracle_text = "You may play an additional land on each of your turns."

    perms = permission_rules.derive_permissions(forest_axis1, game_state).permissions

    assert "may_play_additional_land_per_turn" in perms


# ------------------------------------------------------------
# KEYWORD-BASED PERMISSIONS
# ------------------------------------------------------------

def test_flashback_keyword(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Flashback {3}{G}"

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "has_flashback" in perms
    assert "may_cast_from_graveyard" in perms


def test_escape_keyword(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Escape—{4}{G}, Exile two other cards from your graveyard."

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "has_escape" in perms
    assert "may_cast_from_graveyard" in perms


def test_retrace_keyword(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Retrace"

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "has_retrace" in perms
    assert "may_cast_from_graveyard" in perms


def test_jump_start_keyword(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Jump-start"

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "has_jump_start" in perms
    assert "may_cast_from_graveyard" in perms


def test_foretell_keyword(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Foretell {1}{G}"

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "has_foretell" in perms


def test_unearth_keyword(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Unearth {2}{G}"

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "has_unearth" in perms
    assert "may_activate_from_graveyard" in perms


# ------------------------------------------------------------
# CONTINUOUS EFFECT PERMISSIONS
# ------------------------------------------------------------

def test_continuous_effect_extra_land_play(forest_axis1, game_state):
    game_state.continuous_effects.append({
        "type": "extra_land_play",
        "applies_to": "you"
    })

    perms = permission_rules.derive_permissions(forest_axis1, game_state).permissions

    assert "may_play_additional_land_per_turn" in perms


def test_continuous_effect_play_lands_from_graveyard(forest_axis1, game_state):
    game_state.continuous_effects.append({
        "type": "play_lands_from_graveyard",
        "applies_to": "you"
    })

    perms = permission_rules.derive_permissions(forest_axis1, game_state).permissions

    assert "may_play_lands_from_graveyard" in perms


def test_continuous_effect_cast_from_graveyard(hydra_axis1, game_state):
    game_state.continuous_effects.append({
        "type": "cast_from_graveyard",
        "applies_to": "all_spells"
    })

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "may_cast_from_graveyard" in perms


def test_continuous_effect_cast_as_flash(hydra_axis1, game_state):
    game_state.continuous_effects.append({
        "type": "cast_as_though_had_flash",
        "applies_to": "all_spells"
    })

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert "may_cast_as_though_had_flash" in perms


# ------------------------------------------------------------
# DEDUPLICATION
# ------------------------------------------------------------

def test_permissions_deduplicate(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Flashback {3}{G}"
    game_state.continuous_effects.append({
        "type": "cast_from_graveyard",
        "applies_to": "all_spells"
    })

    perms = permission_rules.derive_permissions(hydra_axis1, game_state).permissions

    assert perms.count("may_cast_from_graveyard") == 1


# ------------------------------------------------------------
# INTEGRATION WITH AXIS2 BUILDER
# ------------------------------------------------------------

def test_permissions_integrate_with_axis2_builder(hydra_axis1, game_state):
    hydra_axis1.faces[0].oracle_text = "Flashback {3}{G}"

    axis2 = Axis2Builder.build(hydra_axis1, game_state)
    cast_action = axis2.actions["cast_spell"]

    assert "has_flashback" in cast_action.permissions
    assert "may_cast_from_graveyard" in cast_action.permissions
