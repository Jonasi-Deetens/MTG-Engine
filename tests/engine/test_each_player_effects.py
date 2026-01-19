from engine import GameState, PlayerState
from engine.effects import EffectResolver
from engine.state import ResolveContext


def _build_state() -> GameState:
    players = [PlayerState(id=0, life=10), PlayerState(id=1, life=12)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    return game_state


def test_each_player_life_effect():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0)

    result = resolver.apply({"type": "life", "amount": 2, "target": "each_player"}, context)

    assert result["type"] == "life"
    assert len(result["results"]) == 2
    assert game_state.get_player(0).life == 12
    assert game_state.get_player(1).life == 14


def test_each_player_replace_draw():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0)

    result = resolver.apply({"type": "replace_draw", "target": "each_player", "replacementZone": "exile"}, context)

    assert result["type"] == "replace_draw"
    assert len(result["results"]) == 2
    affected = {entry["player_id"] for entry in result["results"]}
    assert affected == {0, 1}

