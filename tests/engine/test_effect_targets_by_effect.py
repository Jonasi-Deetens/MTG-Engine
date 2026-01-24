from engine import GameObject, GameState, PlayerState, ResolveContext
from engine.effects.effect_resolver import EffectGraphResolver
from engine.zones import ZONE_BATTLEFIELD


def test_effect_specific_targets_are_applied():
    players = [PlayerState(id=0, life=20), PlayerState(id=1, life=20)]
    game_state = GameState(players=players)
    creature = GameObject(
        id="creature",
        name="Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(creature)
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
                        "action": {
                            "type": "change_power_toughness",
                            "powerChange": 1,
                            "toughnessChange": 1,
                            "target": "target_creature",
                        },
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
                        "action": {
                            "type": "lose_life",
                            "amount": 3,
                            "target": "player",
                        },
                    },
                },
            },
        ],
    }
    resolver = EffectGraphResolver(game_state)
    context = ResolveContext(
        controller_id=0,
        targets_by_effect={
            "e1": {"target": creature.id},
            "e2": {"target_player": 1},
        },
    )

    result = resolver.resolve(graph, context)

    assert result["e1"]["results"][0]["object_id"] == creature.id
    assert game_state.get_player(1).life == 17

