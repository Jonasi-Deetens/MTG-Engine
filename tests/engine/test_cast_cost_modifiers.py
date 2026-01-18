from engine import GameObject, GameState, PlayerState, TurnManager
from engine.rules import cast_spell, prepare_cast
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def _modifier_graph(amount: int) -> dict:
    return {
        "rootNodeId": "s1",
        "abilityType": "static",
        "nodes": [
            {
                "id": "s1",
                "type": "EFFECT",
                "data": {
                    "appliesTo": "spells_you_cast",
                    "effect": {"type": "modify_cast_cost", "amount": amount},
                },
            },
        ],
        "edges": [],
    }


def test_prepare_cast_applies_cost_reduction():
    game_state = _build_state()
    reducer = GameObject(
        id="reducer",
        name="Reducer",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_modifier_graph(-1)],
    )
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{2}{G}",
    )
    game_state.add_object(reducer)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)

    result = prepare_cast(game_state, turn_manager, player_id=0, object_id=spell.id)

    assert result["cost"]["generic"] == 1


def test_cast_spell_applies_cost_increase():
    game_state = _build_state()
    increaser = GameObject(
        id="increaser",
        name="Increaser",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_modifier_graph(1)],
    )
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{1}{G}",
    )
    game_state.add_object(increaser)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1
    game_state.get_player(0).mana_pool["C"] = 2

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
    )

    assert game_state.stack.items

