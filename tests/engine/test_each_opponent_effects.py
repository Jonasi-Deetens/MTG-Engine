from engine import GameState, PlayerState
from engine.effects import EffectResolver
from engine.state import ResolveContext


def _build_state() -> GameState:
    players = [PlayerState(id=0, life=10), PlayerState(id=1, life=12), PlayerState(id=2, life=8)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    return game_state


def test_each_opponent_lose_life_affects_non_controller():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0)

    result = resolver.apply({"type": "lose_life", "amount": 2, "target": "each_opponent"}, context)

    assert result["type"] == "lose_life"
    assert len(result["results"]) == 2
    assert game_state.get_player(0).life == 10
    assert game_state.get_player(1).life == 10
    assert game_state.get_player(2).life == 6


def test_target_opponent_prefers_explicit_target():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"target_player": 2})

    result = resolver.apply({"type": "lose_life", "amount": 3, "target": "opponent"}, context)

    assert result["type"] == "lose_life"
    assert len(result["results"]) == 1
    assert result["results"][0]["player_id"] == 2
    assert game_state.get_player(1).life == 12
    assert game_state.get_player(2).life == 5

