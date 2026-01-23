import pytest

from engine import CombatState, GameObject, GameState, PlayerState
from engine.combat_damage import resolve_combat_damage
from engine.zones import ZONE_BATTLEFIELD


class _DummyTurnManager:
    def after_player_action(self, player_id: int) -> None:
        return


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def _attach_objects(game_state, objs):
    for obj in objs:
        game_state.add_object(obj)


def test_blocker_order_enforced_for_manual_assignments():
    game_state = _build_state()
    attacker = GameObject(
        id="attacker",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    attacker.is_attacking = True
    b1 = GameObject(
        id="b1",
        name="Blocker 1",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=2,
    )
    b1.is_blocking = True
    b2 = GameObject(
        id="b2",
        name="Blocker 2",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=2,
    )
    b2.is_blocking = True
    _attach_objects(game_state, [attacker, b1, b2])

    game_state.turn.combat_state = CombatState(
        attacking_player_id=0,
        defending_player_id=1,
        attackers=[attacker.id],
        blockers={attacker.id: [b1.id, b2.id]},
    )
    game_state.choices["blocker_order:attacker"] = [b2.id, b1.id]

    with pytest.raises(ValueError):
        resolve_combat_damage(
            game_state,
            _DummyTurnManager(),
            player_id=0,
            damage_assignments={
                attacker.id: {b1.id: 2, b2.id: 1},
            },
        )


def test_trample_deathtouch_requires_lethal_before_player():
    game_state = _build_state()
    attacker = GameObject(
        id="attacker",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    attacker.is_attacking = True
    attacker.keywords = {"Trample", "Deathtouch"}
    b1 = GameObject(
        id="b1",
        name="Blocker 1",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=3,
    )
    b1.is_blocking = True
    b2 = GameObject(
        id="b2",
        name="Blocker 2",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=3,
    )
    b2.is_blocking = True
    _attach_objects(game_state, [attacker, b1, b2])

    game_state.turn.combat_state = CombatState(
        attacking_player_id=0,
        defending_player_id=1,
        attackers=[attacker.id],
        blockers={attacker.id: [b1.id, b2.id]},
    )
    game_state.choices["blocker_order:attacker"] = [b1.id, b2.id]

    with pytest.raises(ValueError):
        resolve_combat_damage(
            game_state,
            _DummyTurnManager(),
            player_id=0,
            damage_assignments={
                attacker.id: {b1.id: 1, "player": 2},
            },
        )


def test_trample_deathtouch_valid_assignment():
    game_state = _build_state()
    attacker = GameObject(
        id="attacker",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    attacker.is_attacking = True
    attacker.keywords = {"Trample", "Deathtouch"}
    b1 = GameObject(
        id="b1",
        name="Blocker 1",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=3,
    )
    b1.is_blocking = True
    b2 = GameObject(
        id="b2",
        name="Blocker 2",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=3,
    )
    b2.is_blocking = True
    _attach_objects(game_state, [attacker, b1, b2])

    game_state.turn.combat_state = CombatState(
        attacking_player_id=0,
        defending_player_id=1,
        attackers=[attacker.id],
        blockers={attacker.id: [b1.id, b2.id]},
    )
    game_state.choices["blocker_order:attacker"] = [b1.id, b2.id]

    resolve_combat_damage(
        game_state,
        _DummyTurnManager(),
        player_id=0,
        damage_assignments={
            attacker.id: {b1.id: 1, b2.id: 1, "player": 1},
        },
    )


def test_combat_damage_assign_to_planeswalker_defender():
    game_state = _build_state()
    attacker = GameObject(
        id="attacker",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    attacker.is_attacking = True
    planeswalker = GameObject(
        id="pw1",
        name="Walker",
        owner_id=1,
        controller_id=1,
        types=["Planeswalker"],
        zone=ZONE_BATTLEFIELD,
        power=None,
        toughness=None,
    )
    planeswalker.counters["loyalty"] = 3
    _attach_objects(game_state, [attacker, planeswalker])

    game_state.turn.combat_state = CombatState(
        attacking_player_id=0,
        defending_player_id=1,
        defending_object_id=planeswalker.id,
        attackers=[attacker.id],
        blockers={attacker.id: []},
    )

    resolve_combat_damage(
        game_state,
        _DummyTurnManager(),
        player_id=0,
        damage_assignments={
            attacker.id: {"defender": 3},
        },
    )

    # Planeswalker takes 3 damage, reducing loyalty to 0, and dies to SBAs
    # Check it's in graveyard (loyalty may be cleared when moving zones)
    from engine.zones import ZONE_GRAVEYARD
    assert planeswalker.zone == ZONE_GRAVEYARD or planeswalker.counters.get("loyalty", 0) == 0

