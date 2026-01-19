import pytest

from engine import AbilityGraphRuntimeAdapter, GameState, PlayerState, ResolveContext
from engine.choices import validate_modal_choices


def _modal_graph():
    return {
        "rootNodeId": "act-1",
        "abilityType": "activated",
        "modal": {
            "min": 1,
            "max": 1,
            "modes": [{"id": "mode-a", "label": "Mode A"}, {"id": "mode-b", "label": "Mode B"}],
        },
        "nodes": [
            {"id": "act-1", "type": "ACTIVATED", "data": {"cost": ""}},
            {
                "id": "e1",
                "type": "EFFECT",
                "data": {"type": "lose_life", "amount": 3, "target": "player", "modeId": "mode-a"},
            },
            {
                "id": "e2",
                "type": "EFFECT",
                "data": {"type": "lose_life", "amount": 5, "target": "player", "modeId": "mode-b"},
            },
        ],
        "edges": [
            {"from_": "act-1", "to": "e1"},
            {"from_": "act-1", "to": "e2"},
        ],
    }


def test_modal_choice_requires_selection():
    graph = _modal_graph()
    with pytest.raises(ValueError, match="Missing modal choices"):
        validate_modal_choices(graph, {"choices": {}})


def test_modal_choice_rejects_invalid_modes():
    graph = _modal_graph()
    with pytest.raises(ValueError, match="Invalid modal choice"):
        validate_modal_choices(graph, {"choices": {"chosen_modes": ["mode-c"]}})


def test_modal_choice_enforces_count():
    graph = _modal_graph()
    with pytest.raises(ValueError, match="Select at least"):
        validate_modal_choices(graph, {"choices": {"chosen_modes": []}})
    validate_modal_choices(graph, {"choices": {"chosen_modes": ["mode-a"]}})


def test_modal_effects_only_apply_for_selected_modes():
    players = [PlayerState(id=0, life=20), PlayerState(id=1, life=20)]
    game_state = GameState(players=players)
    graph = _modal_graph()
    adapter = AbilityGraphRuntimeAdapter(game_state)
    context = ResolveContext(
        controller_id=0,
        choices={"chosen_modes": ["mode-a"]},
        targets_by_effect={
            "e1": {"target_player": 1},
            "e2": {"target_player": 1},
        },
    )

    result = adapter.resolve(graph, context)

    assert result["status"] == "resolved"
    assert game_state.get_player(1).life == 17

