from engine import GameObject, GameState, PlayerState, TurnManager, Phase, Step
from engine.effects import EffectResolver
from engine.state import ResolveContext
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


def _discard_graph() -> dict:
    return {
        "id": "graph-1",
        "sourceKind": "spell",
        "steps": [
            {
                "id": "step-1",
                "effect": {
                    "id": "eff-1",
                    "initiation": "static",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "discard", "amount": 1, "target": "player"},
                    },
                },
            }
        ],
    }


def test_overload_discard_per_player_choices():
    game_state = _build_state()
    spell = GameObject(
        id="spell",
        name="Overload Discard",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{1}{B}",
    )
    card_a = GameObject(
        id="a",
        name="Card A",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
    )
    card_b = GameObject(
        id="b",
        name="Card B",
        owner_id=1,
        controller_id=1,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
    )
    game_state.add_object(spell)
    game_state.add_object(card_a)
    game_state.add_object(card_b)
    game_state.get_player(0).mana_pool["B"] = 1
    game_state.get_player(0).mana_pool["C"] = 1
    turn_manager = TurnManager(game_state)

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        effect_graph=_discard_graph(),
        context={
            "choices": {
                "alternative_cost_tag": "overload:{1}{B}",
                "discard_ids_by_player": {"0": [card_a.id], "1": [card_b.id]},
            }
        },
    )

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert card_a.zone != ZONE_HAND
    assert card_b.zone != ZONE_HAND


def test_overload_search_uses_per_player_targets():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    game_state.get_player(0).library = ["p0-card"]
    game_state.get_player(1).library = ["p1-card"]
    context = ResolveContext(
        controller_id=0,
        choices={"alternative_cost_tag": "overload"},
        targets={"search_results_by_player": {"0": ["p0-card"], "1": ["p1-card"]}},
    )

    result = resolver.apply({"type": "search", "target": "player"}, context)

    assert result["type"] == "search"
    assert len(result["results"]) == 2
    assert result["results"][0]["found"] == ["p0-card"]
    assert result["results"][1]["found"] == ["p1-card"]


def test_overload_shuffle_returns_multi_player_results():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    game_state.get_player(0).library = ["p0-a", "p0-b", "p0-c"]
    game_state.get_player(1).library = ["p1-a", "p1-b", "p1-c"]
    context = ResolveContext(controller_id=0, choices={"alternative_cost_tag": "overload"})

    result = resolver.apply({"type": "shuffle", "target": "player"}, context)

    assert result["type"] == "shuffle"
    assert len(result["results"]) == 2


def test_overload_draw_targets_all_players():
    from engine.zones import ZONE_LIBRARY
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    # Create actual game objects for drawing
    card_0 = GameObject(id="p0-a", name="Card0", owner_id=0, controller_id=0, types=["Instant"], zone=ZONE_LIBRARY)
    card_1 = GameObject(id="p1-a", name="Card1", owner_id=1, controller_id=1, types=["Instant"], zone=ZONE_LIBRARY)
    game_state.add_object(card_0)
    game_state.add_object(card_1)
    context = ResolveContext(controller_id=0, choices={"alternative_cost_tag": "overload"})

    result = resolver.apply({"type": "draw", "amount": 1, "target": "player"}, context)

    assert result["type"] == "draw"
    assert len(result["results"]) == 2
    assert len(game_state.get_player(0).hand) == 1
    assert len(game_state.get_player(1).hand) == 1


def test_overload_replace_draw_applies_to_each_player():
    game_state = _build_state()
    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, choices={"alternative_cost_tag": "overload"})

    result = resolver.apply({"type": "replace_draw", "target": "player", "replacementZone": "exile"}, context)

    assert result["type"] == "replace_draw"
    assert len(result["results"]) == 2
    affected = {entry["player_id"] for entry in result["results"]}
    assert affected == {0, 1}

