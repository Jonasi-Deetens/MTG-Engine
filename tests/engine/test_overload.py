from engine import GameObject, GameState, PlayerState, TurnManager, Phase, Step
from tests.engine.cost_helpers import mana_cost_data
from engine.rules import cast_spell
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    return game_state


def _damage_graph() -> dict:
    return {
        "rootNodeId": "a1",
        "abilityType": "activated",
        "nodes": [
            {"id": "a1", "type": "ACTIVATED", "data": {"cost": ""}},
            {
                "id": "kw1",
                "type": "KEYWORD",
                "data": {"keyword": "overload", "costs": [{"type": "mana", "cost": mana_cost_data("{1}{R}")}]},
            },
            {"id": "e1", "type": "EFFECT", "data": {"type": "damage", "amount": 2, "target": "target_creature"}},
        ],
        "edges": [{"from_": "a1", "to": "e1"}],
    }


def test_overload_affects_all_creatures():
    game_state = _build_state()
    spell = GameObject(
        id="spell",
        name="Overload Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{1}{R}",
    )
    creature_a = GameObject(
        id="a",
        name="Creature A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature_b = GameObject(
        id="b",
        name="Creature B",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    game_state.add_object(spell)
    game_state.add_object(creature_a)
    game_state.add_object(creature_b)
    game_state.get_player(0).mana_pool["R"] = 1
    game_state.get_player(0).mana_pool["C"] = 1
    turn_manager = TurnManager(game_state)

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        ability_graph=_damage_graph(),
        context={"choices": {"alternative_cost_tag": "overload:{1}{R}"}},
    )

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    # Overload spell dealt 2 damage to all creatures
    # creature_a (2/2) took lethal damage and died
    # creature_b (3/3) took 2 damage and survived
    assert creature_a.zone == "graveyard"  # Died from lethal damage (2 damage >= 2 toughness)
    assert creature_b.damage == 2
    assert creature_b.zone == ZONE_BATTLEFIELD

