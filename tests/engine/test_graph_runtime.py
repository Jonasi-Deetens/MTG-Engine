from engine import AbilityGraphRuntimeAdapter, GameState, PlayerState, ResolveContext
from engine.effects import EffectResolver


def test_resolve_damage_effect():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    adapter = AbilityGraphRuntimeAdapter(game_state)

    graph = {
        "rootNodeId": "trigger-1",
        "abilityType": "triggered",
        "nodes": [
            {"id": "trigger-1", "type": "TRIGGER", "data": {"event": "deals_damage"}},
            {"id": "effect-1", "type": "EFFECT", "data": {"type": "damage", "amount": 3, "target": "player"}},
        ],
        "edges": [{"from_": "trigger-1", "to": "effect-1"}],
    }

    context = ResolveContext(controller_id=0, targets={"player_id": 0})
    result = adapter.resolve(graph, context)

    assert result["status"] == "resolved"
    assert players[0].life == 17


def test_condition_blocks_resolution():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    adapter = AbilityGraphRuntimeAdapter(game_state)

    graph = {
        "rootNodeId": "trigger-1",
        "abilityType": "triggered",
        "nodes": [
            {"id": "trigger-1", "type": "TRIGGER", "data": {"event": "enters_battlefield"}},
            {"id": "condition-1", "type": "CONDITION", "data": {"type": "life_total", "comparison": "<", "value": 10}},
            {"id": "effect-1", "type": "EFFECT", "data": {"type": "draw", "amount": 1}},
        ],
        "edges": [
            {"from_": "trigger-1", "to": "condition-1"},
            {"from_": "condition-1", "to": "effect-1"},
        ],
    }

    context = ResolveContext(controller_id=0)
    result = adapter.resolve(graph, context)

    assert result["status"] == "condition_failed"


def test_draw_from_empty_library_causes_loss():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"player_id": 0})

    result = resolver.apply({"type": "draw", "amount": 1}, context)

    assert result["type"] == "draw"
    assert players[0].has_lost is True
    assert players[0].removed_from_game is True
