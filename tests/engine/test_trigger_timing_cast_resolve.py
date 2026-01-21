from engine import AbilityRegistry, GameObject, GameState, PlayerState, TurnManager, Phase, Step
from engine.rules import cast_spell
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND


def _trigger_graph(event: str) -> dict:
    return {
        "rootNodeId": "t1",
        "abilityType": "triggered",
        "nodes": [
            {"id": "t1", "type": "TRIGGER", "data": {"event": event, "scope": "any"}},
            {"id": "e1", "type": "EFFECT", "data": {"type": "life", "amount": 0}},
        ],
        "edges": [{"from_": "t1", "to": "e1"}],
    }


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    return game_state


def test_trigger_on_cast_goes_on_stack_before_priority():
    game_state = _build_state()
    watcher = GameObject(
        id="watcher",
        name="Watcher",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph("spell_cast")],
    )
    spell = GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(watcher)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1
    AbilityRegistry(game_state)

    cast_spell(game_state, turn_manager, player_id=0, object_id=spell.id)

    assert game_state.stack.items
    assert game_state.stack.items[-1].kind == "ability_graph"


def test_trigger_from_resolution_put_on_stack_before_priority():
    game_state = _build_state()
    watcher = GameObject(
        id="watcher",
        name="Watcher",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[_trigger_graph("enters_battlefield")],
    )
    creature_spell = GameObject(
        id="creature",
        name="Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_HAND,
        mana_cost="{G}",
        power=2,
        toughness=2,
    )
    game_state.add_object(watcher)
    game_state.add_object(creature_spell)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1
    AbilityRegistry(game_state)

    cast_spell(game_state, turn_manager, player_id=0, object_id=creature_spell.id)
    current = turn_manager.priority.current
    turn_manager.handle_player_pass(current)
    turn_manager.handle_player_pass(turn_manager.priority.current)

    assert game_state.stack.items
    assert game_state.stack.items[-1].kind == "ability_graph"

