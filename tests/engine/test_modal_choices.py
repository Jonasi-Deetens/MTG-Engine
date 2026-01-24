import pytest

from engine import GameState, PlayerState, ResolveContext
from engine.choices import validate_modal_choices_effect_graph
from engine.effects.effect_resolver import EffectGraphResolver


def _modal_graph():
    return {
        "id": "graph-1",
        "sourceKind": "permanent",
        "modal": {
            "min": 1,
            "max": 1,
            "modes": [{"id": "mode-a", "label": "Mode A"}, {"id": "mode-b", "label": "Mode B"}],
        },
        "steps": [
            {
                "id": "step-root",
                "effect": {
                    "id": "eff-root",
                    "initiation": "activated",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "cost": {"items": []},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "draw", "amount": 0},
                    },
                },
                "nextByMode": {
                    "mode-a": "step-a",
                    "mode-b": "step-b",
                },
            },
            {
                "id": "step-a",
                "effect": {
                    "id": "eff-a",
                    "initiation": "activated",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "cost": {"items": []},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "lose_life", "amount": 3, "target": "player"},
                    },
                },
            },
            {
                "id": "step-b",
                "effect": {
                    "id": "eff-b",
                    "initiation": "activated",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "cost": {"items": []},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "lose_life", "amount": 5, "target": "player"},
                    },
                },
            },
        ],
    }


def test_modal_choice_requires_selection():
    graph = _modal_graph()
    with pytest.raises(ValueError, match="Missing modal choices"):
        validate_modal_choices_effect_graph(graph, {"choices": {}})


def test_modal_choice_rejects_invalid_modes():
    graph = _modal_graph()
    with pytest.raises(ValueError, match="Invalid modal choice"):
        validate_modal_choices_effect_graph(graph, {"choices": {"chosen_modes": ["mode-c"]}})


def test_modal_choice_enforces_count():
    graph = _modal_graph()
    with pytest.raises(ValueError, match="Missing modal choices|Select at least"):
        validate_modal_choices_effect_graph(graph, {"choices": {"chosen_modes": []}})
    validate_modal_choices_effect_graph(graph, {"choices": {"chosen_modes": ["mode-a"]}})


def test_modal_effects_only_apply_for_selected_modes():
    players = [PlayerState(id=0, life=20), PlayerState(id=1, life=20)]
    game_state = GameState(players=players)
    graph = _modal_graph()
    resolver = EffectGraphResolver(game_state)
    context = ResolveContext(
        controller_id=0,
        choices={"chosen_modes": ["mode-a"]},
        targets_by_effect={
            "step-a": {"target_player": 1},
            "step-b": {"target_player": 1},
        },
    )

    result = resolver.resolve(graph, context)

    assert "step-a" in result
    assert game_state.get_player(1).life == 17

