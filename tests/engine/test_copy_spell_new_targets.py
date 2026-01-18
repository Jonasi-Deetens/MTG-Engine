from engine import GameObject, GameState, PlayerState
from engine.effects import EffectResolver
from engine.stack import StackItem
from engine.state import ResolveContext
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND


def test_copy_spell_uses_new_targets_when_provided():
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    resolver = EffectResolver(game_state)
    creature_a = GameObject(
        id="a",
        name="Creature A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    creature_b = GameObject(
        id="b",
        name="Creature B",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    spell = GameObject(
        id="spell",
        name="Targeted Spell",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
    )
    game_state.add_object(creature_a)
    game_state.add_object(creature_b)
    game_state.add_object(spell)
    game_state.stack.push(
        StackItem(
            kind="spell",
            payload={
                "object_id": spell.id,
                "context": {"targets": {"target": creature_a.id}},
            },
            controller_id=0,
        )
    )
    context = ResolveContext(
        controller_id=0,
        targets={"target": spell.id},
        choices={"copy_choose_new_targets": True, "copy_targets": {"target": creature_b.id}},
    )

    result = resolver.apply({"type": "copy_spell", "target": "spell", "chooseNewTargets": True}, context)

    assert result["type"] == "copy_spell"
    copied = game_state.stack.items[-1].payload
    assert copied.get("copy_of") == spell.id
    assert copied.get("context", {}).get("targets", {}).get("target") == creature_b.id


def test_copy_ability_graph_uses_new_targets_by_effect():
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    resolver = EffectResolver(game_state)
    creature_a = GameObject(
        id="a",
        name="Creature A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    creature_b = GameObject(
        id="b",
        name="Creature B",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(creature_a)
    game_state.add_object(creature_b)
    graph = {
        "rootNodeId": "act-1",
        "abilityType": "activated",
        "nodes": [
            {"id": "act-1", "type": "ACTIVATED", "data": {"cost": ""}},
            {"id": "e1", "type": "EFFECT", "data": {"type": "damage", "amount": 1, "target": "target_creature"}},
        ],
        "edges": [{"from_": "act-1", "to": "e1"}],
    }
    spell = GameObject(
        id="spell",
        name="Spell Source",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
    )
    game_state.add_object(spell)
    game_state.stack.push(
        StackItem(
            kind="ability_graph",
            payload={
                "graph": graph,
                "context": {"targets_by_effect": {"e1": {"target": creature_a.id}}},
                "source_object_id": spell.id,
            },
            controller_id=0,
        )
    )
    context = ResolveContext(
        controller_id=0,
        targets={"target": spell.id},
        choices={
            "copy_choose_new_targets": True,
            "copy_targets_by_effect": {"e1": {"target": creature_b.id}},
        },
    )

    result = resolver.apply({"type": "copy_spell", "target": "spell", "chooseNewTargets": True}, context)

    assert result["type"] == "copy_spell"
    copied = game_state.stack.items[-1].payload
    assert copied.get("context", {}).get("targets_by_effect", {}).get("e1", {}).get("target") == creature_b.id


def test_copy_spell_multiple_copies_use_per_copy_targets():
    players = [PlayerState(id=0)]
    game_state = GameState(players=players)
    resolver = EffectResolver(game_state)
    creature_a = GameObject(
        id="a",
        name="Creature A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    creature_b = GameObject(
        id="b",
        name="Creature B",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    creature_c = GameObject(
        id="c",
        name="Creature C",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    spell = GameObject(
        id="spell",
        name="Targeted Spell",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
    )
    game_state.add_object(creature_a)
    game_state.add_object(creature_b)
    game_state.add_object(creature_c)
    game_state.add_object(spell)
    game_state.stack.push(
        StackItem(
            kind="spell",
            payload={
                "object_id": spell.id,
                "context": {"targets": {"target": creature_a.id}},
            },
            controller_id=0,
        )
    )
    context = ResolveContext(
        controller_id=0,
        targets={"target": spell.id},
        choices={
            "copy_choose_new_targets": True,
            "copy_targets_list": [{"target": creature_b.id}, {"target": creature_c.id}],
        },
    )

    result = resolver.apply({"type": "copy_spell", "target": "spell", "amount": 2, "chooseNewTargets": True}, context)

    assert result["copies"] == 2
    copied_targets = [
        item.payload.get("context", {}).get("targets", {}).get("target")
        for item in game_state.stack.items[-2:]
    ]
    assert set(copied_targets) == {creature_b.id, creature_c.id}


def test_copy_spell_invalid_new_target_raises():
    players = [PlayerState(id=0)]
    game_state = GameState(players=players)
    resolver = EffectResolver(game_state)
    creature_a = GameObject(
        id="a",
        name="Creature A",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    spell = GameObject(
        id="spell",
        name="Targeted Spell",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
    )
    game_state.add_object(creature_a)
    game_state.add_object(spell)
    game_state.stack.push(
        StackItem(
            kind="spell",
            payload={
                "object_id": spell.id,
                "context": {"targets": {"target": creature_a.id}},
            },
            controller_id=0,
        )
    )
    context = ResolveContext(
        controller_id=0,
        targets={"target": spell.id},
        choices={"copy_choose_new_targets": True, "copy_targets": {"target": "missing"}},
    )

    try:
        resolver.apply({"type": "copy_spell", "target": "spell", "chooseNewTargets": True}, context)
        assert False, "Expected invalid copy targets to raise."
    except ValueError as exc:
        assert "target" in str(exc).lower()

