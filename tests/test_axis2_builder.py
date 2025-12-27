from axis2.builder import Axis2Builder


# ------------------------------------------------------------
# FOREST TESTS
# ------------------------------------------------------------

def test_forest_play_land_action(forest_axis1, game_state):
    axis2 = Axis2Builder.build(forest_axis1, game_state)

    play_land = axis2.actions["play_land"]
    assert play_land.allowed is True
    assert "Hand" in play_land.zones
    assert play_land.limit_per_turn == 1
    assert play_land.turn_permissions.controller_only is True


def test_forest_cannot_cast_spell(forest_axis1, game_state):
    axis2 = Axis2Builder.build(forest_axis1, game_state)

    cast_spell = axis2.actions["cast_spell"]
    assert cast_spell.allowed is False


def test_forest_zone_permissions(forest_axis1, game_state):
    axis2 = Axis2Builder.build(forest_axis1, game_state)

    perms = axis2.zone_permissions.permissions
    assert "play_land" in perms["Hand"]
    assert "cast_spell" not in perms["Hand"]
    assert "activate_ability" in perms["Battlefield"]


def test_forest_visibility(forest_axis1, game_state):
    axis2 = Axis2Builder.build(forest_axis1, game_state)

    vis = axis2.visibility_constraints
    assert vis.face_down_objects["cannot_be_targeted"] is False
    assert vis.random_selection is False


# ------------------------------------------------------------
# HYDRA TESTS
# ------------------------------------------------------------

def test_hydra_cast_spell_action(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    cast_spell = axis2.actions["cast_spell"]
    assert cast_spell.allowed is True
    assert cast_spell.costs.mana == "{5}{G}"
    assert cast_spell.timing.speed == "sorcery"
    assert cast_spell.timing.stack_must_be_empty is True


def test_hydra_zone_permissions(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    perms = axis2.zone_permissions.permissions
    assert "cast_spell" in perms["Hand"]
    assert "play_land" not in perms["Hand"]


def test_hydra_triggers(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    assert len(axis2.triggers) == 1
    trigger = axis2.triggers[0]
    assert trigger.event == "enters_battlefield"
    assert trigger.mandatory is True


def test_hydra_limits(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    # Hydra is not a land → no land limits
    assert len(axis2.limits) == 0


def test_hydra_visibility(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    vis = axis2.visibility_constraints
    assert vis.face_down_objects["cannot_be_targeted"] is False
    assert vis.random_selection is False


# ------------------------------------------------------------
# INTEGRATION TEST
# ------------------------------------------------------------

def test_axis2_full_card_structure(hydra_axis1, game_state):
    axis2 = Axis2Builder.build(hydra_axis1, game_state)

    assert isinstance(axis2.actions, dict)
    assert "cast_spell" in axis2.actions
    assert "play_land" in axis2.actions
    assert "activate_ability" in axis2.actions
    assert "special_actions" in axis2.actions

    assert isinstance(axis2.zone_permissions.permissions, dict)
    assert isinstance(axis2.triggers, list)
    assert isinstance(axis2.global_restrictions, list)
    assert isinstance(axis2.limits, list)
    assert isinstance(axis2.visibility_constraints, object)
