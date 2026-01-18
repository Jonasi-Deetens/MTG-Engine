from engine import GameObject, GameState, PlayerState, TurnManager
from engine.rules import cast_spell
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def _damage_graph() -> dict:
    return {
        "rootNodeId": "a1",
        "abilityType": "activated",
        "nodes": [
            {"id": "a1", "type": "ACTIVATED", "data": {"cost": ""}},
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
    spell.oracle_text = "Overload {1}{R}"
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

    assert creature_a.damage == 2
    assert creature_b.damage == 2

