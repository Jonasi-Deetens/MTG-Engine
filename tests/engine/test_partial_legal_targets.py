from engine import GameObject, GameState, PlayerState, TurnManager
from engine.stack import StackItem
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD


def _build_state() -> GameState:
    players = [PlayerState(id=0, life=20), PlayerState(id=1, life=20)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def test_partial_legal_targets_resolve_for_legal_only():
    game_state = _build_state()
    source = GameObject(
        id="src",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    legal = GameObject(
        id="legal",
        name="Legal",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    illegal = GameObject(
        id="illegal",
        name="Illegal",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_GRAVEYARD,
    )
    game_state.add_object(source)
    game_state.add_object(legal)
    game_state.add_object(illegal)
    graph = {
        "id": "graph-1",
        "sourceKind": "permanent",
        "steps": [
            {
                "id": "e1",
                "effect": {
                    "id": "eff-1",
                    "initiation": "activated",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "cost": {"items": []},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "damage", "amount": 2, "target": "target_creature"},
                    },
                },
            }
        ],
    }
    game_state.stack.push(
        StackItem(
            kind="effect_graph",
            payload={
                "graph": graph,
                "context": {
                    "source_id": source.id,
                    "controller_id": 0,
                    "targets": {"targets": [legal.id, illegal.id]},
                    "required_targets_by_effect": {"_global": ["target"]},
                },
                "source_object_id": source.id,
            },
            controller_id=0,
        )
    )
    turn_manager = TurnManager(game_state)

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert game_state.objects[legal.id].damage == 2
    assert game_state.objects[illegal.id].damage == 0


def test_partial_legal_targets_per_effect_allows_resolution():
    game_state = _build_state()
    source = GameObject(
        id="src",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    illegal = GameObject(
        id="illegal",
        name="Illegal",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_GRAVEYARD,
    )
    game_state.add_object(source)
    game_state.add_object(illegal)
    graph = {
        "id": "graph-1",
        "sourceKind": "permanent",
        "steps": [
            {
                "id": "e1",
                "effect": {
                    "id": "eff-1",
                    "initiation": "activated",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "cost": {"items": []},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "damage", "amount": 2, "target": "target_creature"},
                    },
                },
                "next": ["e2"],
            },
            {
                "id": "e2",
                "effect": {
                    "id": "eff-2",
                    "initiation": "activated",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "cost": {"items": []},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "lose_life", "amount": 1, "target": "player"},
                    },
                },
            },
        ],
    }
    game_state.stack.push(
        StackItem(
            kind="effect_graph",
            payload={
                "graph": graph,
                "context": {
                    "source_id": source.id,
                    "controller_id": 0,
                    "targets_by_effect": {
                        "e1": {"target": illegal.id},
                        "e2": {"target_player": 1},
                    },
                    "required_targets_by_effect": {"e1": ["target"], "e2": ["target"]},
                },
                "source_object_id": source.id,
            },
            controller_id=0,
        )
    )
    turn_manager = TurnManager(game_state)

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert game_state.get_player(1).life == 19

