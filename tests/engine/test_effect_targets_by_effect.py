from engine import AbilityGraphRuntimeAdapter, GameObject, GameState, PlayerState, ResolveContext
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
        "rootNodeId": "act-1",
        "abilityType": "activated",
        "nodes": [
            {"id": "act-1", "type": "ACTIVATED", "data": {"cost": ""}},
            {"id": "e1", "type": "EFFECT", "data": {"type": "change_power_toughness", "powerChange": 1, "toughnessChange": 1, "target": "target_creature"}},
            {"id": "e2", "type": "EFFECT", "data": {"type": "lose_life", "amount": 3, "target": "player"}},
        ],
        "edges": [
            {"from_": "act-1", "to": "e1"},
            {"from_": "e1", "to": "e2"},
        ],
    }
    adapter = AbilityGraphRuntimeAdapter(game_state)
    context = ResolveContext(
        controller_id=0,
        targets_by_effect={
            "e1": {"target": creature.id},
            "e2": {"target_player": 1},
        },
    )

    result = adapter.resolve(graph, context)

    assert result["status"] == "resolved"
    assert result["effects"][0]["results"][0]["object_id"] == creature.id
    assert game_state.get_player(1).life == 17

