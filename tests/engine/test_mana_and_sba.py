import pytest

from engine import GameObject, GameState, PlayerState, TurnManager
from engine.continuous import apply_continuous_effects
from engine.rules import activate_mana_ability, cast_spell
from engine.sba import apply_state_based_actions
from engine.turn import Phase, Step
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND, ZONE_GRAVEYARD


def _build_game_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def test_activate_mana_ability_and_cast_spell():
    game_state = _build_game_state()
    forest = GameObject(
        id="land_1",
        name="Forest",
        owner_id=0,
        controller_id=0,
        types=["Land"],
        zone=ZONE_BATTLEFIELD,
        type_line="Basic Land — Forest",
    )
    spell = GameObject(
        id="spell_1",
        name="Test Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(forest)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)

    with pytest.raises(ValueError):
        cast_spell(game_state, turn_manager, player_id=0, object_id=spell.id)

    activate_mana_ability(game_state, turn_manager, player_id=0, object_id=forest.id)
    cast_spell(game_state, turn_manager, player_id=0, object_id=spell.id)
    assert game_state.stack.items


def test_continuous_effects_and_sba():
    game_state = _build_game_state()
    creature = GameObject(
        id="creature_1",
        name="Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
        base_power=2,
        base_toughness=2,
    )
    game_state.add_object(creature)
    creature.counters["+1/+1"] = 2
    apply_continuous_effects(game_state)
    assert creature.power == 4
    assert creature.toughness == 4

    creature.damage = 5
    apply_state_based_actions(game_state)
    assert creature.zone == ZONE_GRAVEYARD


