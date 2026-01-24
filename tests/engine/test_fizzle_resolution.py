from engine import GameObject, GameState, PlayerState, TurnManager
from engine.stack import StackItem
from engine.zones import ZONE_BATTLEFIELD, ZONE_EXILE, ZONE_GRAVEYARD


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def test_activated_ability_fizzle_does_not_move_source():
    game_state = _build_state()
    obj = GameObject(
        id="creature",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(obj)
    turn_manager = TurnManager(game_state)
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
                        "action": {"type": "damage", "amount": 1, "target": "target_creature"},
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
                "context": {"source_id": obj.id, "controller_id": 0, "targets": {}},
                "source_object_id": obj.id,
            },
            controller_id=0,
        )
    )

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert game_state.objects[obj.id].zone == ZONE_BATTLEFIELD


def test_spell_ability_graph_fizzle_uses_destination_zone():
    game_state = _build_state()
    spell = GameObject(
        id="spell",
        name="Targeted Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone="stack",
    )
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    graph = {
        "id": "graph-1",
        "sourceKind": "spell",
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
                        "action": {"type": "damage", "amount": 1, "target": "target_creature"},
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
                "context": {"source_id": spell.id, "controller_id": 0, "targets": {}},
                "source_object_id": spell.id,
                "destination_zone": ZONE_EXILE,
            },
            controller_id=0,
        )
    )

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert game_state.objects[spell.id].zone == ZONE_EXILE

