from engine import AbilityGraphRuntimeAdapter, GameObject, GameState, PlayerState, ResolveContext
from engine.effects import EffectResolver
from engine.zones import ZONE_BATTLEFIELD, ZONE_LIBRARY


def test_resolve_damage_effect():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    # Damage effects require a source object
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(source)
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

    context = ResolveContext(controller_id=0, source_id=source.id, targets={"player_id": 0})
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


def test_runtime_draw_each_uses_apnap():
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 1
    # Create actual game objects for library cards
    for player in game_state.players:
        for i in range(1, 3):
            card_id = f"card_{player.id}_{i}"
            card = GameObject(
                id=card_id,
                name=f"Card {player.id}-{i}",
                owner_id=player.id,
                controller_id=player.id,
                types=["Instant"],
                zone=ZONE_LIBRARY,
            )
            game_state.add_object(card)
            player.library.append(card_id)
    graph = {
        "rootNodeId": "trigger-1",
        "abilityType": "triggered",
        "nodes": [
            {"id": "trigger-1", "type": "TRIGGER", "data": {"event": "enters_battlefield"}},
            {"id": "effect-1", "type": "EFFECT", "data": {"type": "draw_each", "amount": 1}},
        ],
        "edges": [{"from_": "trigger-1", "to": "effect-1"}],
    }
    adapter = AbilityGraphRuntimeAdapter(game_state)
    context = ResolveContext(controller_id=0)

    result = adapter.resolve(graph, context)

    assert result["effects"][0]["type"] == "draw_each"
    assert len(game_state.get_player(0).hand) == 1
    assert len(game_state.get_player(1).hand) == 1