from engine import GameObject, GameState, PlayerState
from engine.damage import apply_damage_to_object
from engine.zones import ZONE_BATTLEFIELD


def _build_game_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def test_prevent_damage_effect():
    game_state = _build_game_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    target = GameObject(
        id="target",
        name="Target",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    target.temporary_effects.append({"prevent_damage": 2})
    game_state.add_object(source)
    game_state.add_object(target)

    apply_damage_to_object(game_state, source, target, 3)
    assert target.damage == 1


def test_redirect_damage_effect():
    game_state = _build_game_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    target = GameObject(
        id="target",
        name="Target",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    redirect = GameObject(
        id="redirect",
        name="Redirect",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    game_state.add_object(source)
    game_state.add_object(target)
    game_state.add_object(redirect)
    game_state.replacement_effects.append(
        {"type": "redirect_damage", "source": source.id, "redirect": redirect.id, "amount": 3}
    )

    apply_damage_to_object(game_state, source, target, 3)
    assert target.damage == 0
    assert redirect.damage == 3


