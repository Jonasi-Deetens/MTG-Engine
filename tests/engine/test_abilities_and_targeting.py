import pytest

from engine import GameObject, GameState, PlayerState, ResolveContext
from engine.ability_registry import AbilityRegistry
from engine.events import Event
from engine.continuous import apply_continuous_effects
from engine.effects import EffectResolver
from engine.sba import apply_state_based_actions
from engine.targets import validate_targets
from engine.turn import Phase, Step
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD


def _build_game_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    game_state.turn.active_player_index = 0
    return game_state


def test_triggered_ability_pushes_stack_item():
    game_state = _build_game_state()
    creature = GameObject(
        id="creature_1",
        name="Test Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        ability_graphs=[
            {
                "rootNodeId": "trigger-1",
                "abilityType": "triggered",
                "nodes": [
                    {"id": "trigger-1", "type": "TRIGGER", "data": {"event": "enters_battlefield"}},
                    {"id": "effect-1", "type": "EFFECT", "data": {"type": "life", "amount": 1}},
                ],
                "edges": [{"from": "trigger-1", "to": "effect-1"}],
            }
        ],
    )
    game_state.add_object(creature)
    AbilityRegistry(game_state)

    game_state.event_bus.publish(Event(type="enters_battlefield", payload={"object_id": creature.id}))
    assert len(game_state.stack.items) == 1
    assert game_state.stack.items[0].kind == "ability_graph"


def test_validate_targets_rejects_hexproof():
    game_state = _build_game_state()
    protected = GameObject(
        id="hexproof_1",
        name="Hexproof Creature",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        keywords={"Hexproof"},
    )
    game_state.add_object(protected)

    context = type("Ctx", (), {})()
    context.targets = {"target": protected.id}
    context.controller_id = 0

    with pytest.raises(ValueError):
        validate_targets(game_state, context)


def test_validate_targets_rejects_shroud():
    game_state = _build_game_state()
    protected = GameObject(
        id="shroud_1",
        name="Shroud Creature",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        keywords={"Shroud"},
    )
    game_state.add_object(protected)

    context = type("Ctx", (), {})()
    context.targets = {"target": protected.id}
    context.controller_id = 1

    with pytest.raises(ValueError):
        validate_targets(game_state, context)


def test_scry_reorders_library():
    game_state = _build_game_state()
    player = game_state.get_player(0)
    cards = ["card_1", "card_2", "card_3", "card_4"]
    player.library = list(cards)
    resolver = EffectResolver(game_state)
    context = ResolveContext(
        controller_id=0,
        choices={"scry": {"top": ["card_2"], "bottom": ["card_1"]}},
    )

    result = resolver.apply({"type": "scry", "amount": 2}, context)

    assert result["type"] == "scry"
    assert player.library == ["card_2", "card_3", "card_4", "card_1"]


def test_shroud_prevents_aura_attachment():
    game_state = _build_game_state()
    protected = GameObject(
        id="shroud_target",
        name="Shroud Creature",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        keywords={"Shroud"},
    )
    aura = GameObject(
        id="aura_1",
        name="Aura",
        owner_id=0,
        controller_id=0,
        types=["Enchantment", "Aura"],
        zone=ZONE_BATTLEFIELD,
        attached_to=protected.id,
    )
    game_state.add_object(protected)
    game_state.add_object(aura)

    apply_state_based_actions(game_state)

    assert aura.zone == ZONE_GRAVEYARD


def test_validate_targets_uses_triggering_source_for_protection():
    game_state = _build_game_state()
    source = GameObject(
        id="prot_source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        colors=["Red"],
    )
    protected = GameObject(
        id="prot_target",
        name="Protected",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        protections={"Red"},
    )
    game_state.add_object(source)
    game_state.add_object(protected)

    context = type("Ctx", (), {})()
    context.targets = {"target": protected.id}
    context.controller_id = 0
    context.triggering_source_id = source.id
    context.triggering_spell_id = None
    context.triggering_aura_id = None

    with pytest.raises(ValueError):
        validate_targets(game_state, context)


def test_validate_targets_rejects_removed_player():
    game_state = _build_game_state()
    removed = game_state.get_player(1)
    removed.removed_from_game = True

    context = type("Ctx", (), {})()
    context.targets = {"target_player": 1}
    context.controller_id = 0
    context.triggering_source_id = None
    context.triggering_spell_id = None
    context.triggering_aura_id = None

    with pytest.raises(ValueError):
        validate_targets(game_state, context)


def test_flicker_clears_battlefield_state():
    game_state = _build_game_state()
    creature = GameObject(
        id="flicker_target",
        name="Flicker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature.damage = 2
    creature.tapped = True
    creature.counters = {"+1/+1": 2}
    creature.temporary_effects = [{"type": "gain_keyword", "keyword": "Haste"}]
    creature.protections = {"Red"}
    game_state.add_object(creature)

    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"target": creature.id})
    result = resolver.apply({"type": "flicker", "target": "target"}, context)

    assert result["type"] == "flicker"
    assert creature.zone == ZONE_BATTLEFIELD
    assert creature.damage == 0
    assert creature.tapped is False
    assert creature.counters == {}
    assert creature.temporary_effects == []
    assert creature.protections == set()


def test_attach_respects_illegal_targets():
    game_state = _build_game_state()
    creature = GameObject(
        id="equip_target",
        name="Creature",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        keywords={"Shroud"},
    )
    equipment = GameObject(
        id="equipment",
        name="Equipment",
        owner_id=0,
        controller_id=0,
        types=["Artifact", "Equipment"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(creature)
    game_state.add_object(equipment)

    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"target": equipment.id, "attach_to": creature.id})
    result = resolver.apply({"type": "attach", "target": "target", "attachTo": "attach_to"}, context)

    assert result["type"] == "attach"
    assert equipment.attached_to is None


def test_flicker_returns_under_owner_control():
    game_state = _build_game_state()
    creature = GameObject(
        id="flicker_control",
        name="Flicker Target",
        owner_id=0,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    game_state.add_object(creature)

    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=1, targets={"target": creature.id})
    result = resolver.apply({"type": "flicker", "target": "target"}, context)

    assert result["type"] == "flicker"
    assert creature.zone == ZONE_BATTLEFIELD
    assert creature.controller_id == creature.owner_id


def test_phase_out_preserves_attachments():
    game_state = _build_game_state()
    creature = GameObject(
        id="phase_target",
        name="Phase Target",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    aura = GameObject(
        id="phase_aura",
        name="Aura",
        owner_id=0,
        controller_id=0,
        types=["Enchantment", "Aura"],
        zone=ZONE_BATTLEFIELD,
        attached_to=creature.id,
    )
    equipment = GameObject(
        id="phase_equip",
        name="Equipment",
        owner_id=0,
        controller_id=0,
        types=["Artifact", "Equipment"],
        zone=ZONE_BATTLEFIELD,
        attached_to=creature.id,
    )
    game_state.add_object(creature)
    game_state.add_object(aura)
    game_state.add_object(equipment)

    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"target": creature.id})
    result = resolver.apply({"type": "phase_out", "target": "target"}, context)

    assert result["type"] == "phase_out"
    assert creature.phased_out is True
    assert aura.phased_out is True
    assert equipment.phased_out is True
    apply_state_based_actions(game_state)
    assert aura.zone == ZONE_BATTLEFIELD
    assert equipment.zone == ZONE_BATTLEFIELD
    assert aura.attached_to == creature.id
    assert equipment.attached_to == creature.id


def test_phase_out_removes_from_combat():
    game_state = _build_game_state()
    creature = GameObject(
        id="phase_combat",
        name="Combatant",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature.is_attacking = True
    game_state.add_object(creature)

    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"target": creature.id})
    result = resolver.apply({"type": "phase_out", "target": "target"}, context)

    assert result["type"] == "phase_out"
    assert creature.phased_out is True
    assert creature.is_attacking is False


def test_transform_removes_from_combat():
    game_state = _build_game_state()
    creature = GameObject(
        id="transform_target",
        name="Transform",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature.tapped = True
    creature.is_attacking = True
    game_state.add_object(creature)

    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"target": creature.id})
    result = resolver.apply({"type": "transform", "target": "target"}, context)

    assert result["type"] == "transform"
    assert creature.transformed is True
    assert creature.tapped is False
    assert creature.is_attacking is False


def test_change_control_removes_from_combat():
    game_state = _build_game_state()
    creature = GameObject(
        id="control_target",
        name="Control",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature.is_attacking = True
    game_state.add_object(creature)

    resolver = EffectResolver(game_state)
    context = ResolveContext(
        controller_id=1,
        targets={"target": creature.id, "new_controller_id": 1},
    )
    result = resolver.apply({"type": "change_control", "target": "target"}, context)

    assert result["type"] == "change_control"
    assert creature.controller_id == 1
    assert creature.is_attacking is False


def test_temporary_control_change_removes_from_combat():
    game_state = _build_game_state()
    creature = GameObject(
        id="temp_control_target",
        name="Temp Control",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature.is_attacking = True
    creature.temporary_effects = [
        {"type": "set_controller", "controller_id": 1, "duration": "until_end_of_turn"}
    ]
    game_state.add_object(creature)

    apply_continuous_effects(game_state)

    assert creature.controller_id == 1
    assert creature.is_attacking is False


def test_type_change_removes_from_combat():
    game_state = _build_game_state()
    creature = GameObject(
        id="type_change_target",
        name="Type Change",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature.is_attacking = True
    creature.temporary_effects = [
        {"type": "set_types", "types": ["Artifact"], "duration": "until_end_of_turn"}
    ]
    game_state.add_object(creature)

    apply_continuous_effects(game_state)

    assert "Creature" not in creature.types
    assert creature.is_attacking is False


