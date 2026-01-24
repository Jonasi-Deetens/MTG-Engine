from engine import GameObject, GameState, PlayerState, ResolveContext
from engine.effects import EffectResolver
from engine.effects.effect_resolver import EffectGraphResolver
from engine.zones import ZONE_BATTLEFIELD, ZONE_LIBRARY


def _one_shot_graph(step_id: str, action: dict, *, initiation: str = "triggered", trigger_event: str = "enters_battlefield") -> dict:
    effect = {
        "id": f"{step_id}-effect",
        "initiation": initiation,
        "resolution": "stack",
        "persistence": "instant",
        "tags": [],
        "conditions": [],
        "effect": {
            "kind": "one_shot",
            "action": action,
        },
    }
    if initiation == "triggered":
        effect["trigger"] = {"event": trigger_event}
    if initiation == "activated":
        effect["cost"] = {"items": []}
    return {
        "id": "graph-1",
        "sourceKind": "permanent",
        "steps": [
            {
                "id": step_id,
                "effect": effect,
            }
        ],
    }


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
    resolver = EffectGraphResolver(game_state)
    graph = _one_shot_graph(
        "step-1",
        {"type": "damage", "amount": 3, "target": "player"},
        initiation="triggered",
        trigger_event="deals_damage",
    )

    context = ResolveContext(controller_id=0, source_id=source.id, targets={"player_id": 0})
    result = resolver.resolve(graph, context)

    assert result["step-1"]["type"] == "damage"
    assert players[0].life == 17


def test_condition_blocks_resolution():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    resolver = EffectGraphResolver(game_state)
    graph = _one_shot_graph(
        "step-1",
        {
            "type": "draw",
            "amount": 1,
            "condition": {"type": "life_total", "comparison": "<", "value": 10},
        },
        initiation="triggered",
    )

    context = ResolveContext(controller_id=0)
    result = resolver.resolve(graph, context)

    assert result["step-1"]["status"] == "condition_failed"


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
    graph = _one_shot_graph(
        "step-1",
        {"type": "draw_each", "amount": 1},
        initiation="triggered",
    )
    resolver = EffectGraphResolver(game_state)
    context = ResolveContext(controller_id=0)

    result = resolver.resolve(graph, context)

    assert result["step-1"]["type"] == "draw_each"
    assert len(game_state.get_player(0).hand) == 1
    assert len(game_state.get_player(1).hand) == 1