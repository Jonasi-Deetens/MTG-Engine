import pytest

from engine import GameObject, GameState, PlayerState, TurnManager, ResolveContext
from engine.continuous import apply_continuous_effects
from engine.effects import EffectResolver
from engine.rules import activate_mana_ability, cast_spell
from engine.sba import apply_state_based_actions
from engine.damage import apply_damage_to_object, apply_damage_to_player
from engine.turn import Phase, Step
from engine.stack import StackItem
from engine.zones import ZONE_BATTLEFIELD, ZONE_HAND, ZONE_GRAVEYARD, ZONE_EXILE


def _build_game_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def test_activate_mana_ability_and_cast_spell():
    game_state = _build_game_state()
    forest = GameObject(
        id="land_1",
        name="Forest",
        owner_id=0,
        controller_id=0,
        types=["Land"],
        zone=ZONE_BATTLEFIELD,
        type_line="Basic Land — Forest",
    )
    spell = GameObject(
        id="spell_1",
        name="Test Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    game_state.add_object(forest)
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)

    with pytest.raises(ValueError):
        cast_spell(game_state, turn_manager, player_id=0, object_id=spell.id)

    activate_mana_ability(game_state, turn_manager, player_id=0, object_id=forest.id)
    cast_spell(game_state, turn_manager, player_id=0, object_id=spell.id)
    assert game_state.stack.items


def test_continuous_effects_and_sba():
    game_state = _build_game_state()
    creature = GameObject(
        id="creature_1",
        name="Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
        base_power=2,
        base_toughness=2,
    )
    game_state.add_object(creature)
    creature.counters["+1/+1"] = 2
    apply_continuous_effects(game_state)
    assert creature.power == 4
    assert creature.toughness == 4

    creature.damage = 5
    apply_state_based_actions(game_state)
    assert creature.zone == ZONE_GRAVEYARD


def test_legend_rule_keeps_one():
    game_state = _build_game_state()
    first = GameObject(
        id="legend_1",
        name="Legend",
        owner_id=0,
        controller_id=0,
        types=["Creature", "Legendary"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    second = GameObject(
        id="legend_2",
        name="Legend",
        owner_id=0,
        controller_id=0,
        types=["Creature", "Legendary"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    game_state.add_object(first)
    game_state.add_object(second)

    apply_state_based_actions(game_state)

    in_battlefield = [obj for obj in (first, second) if obj.zone == ZONE_BATTLEFIELD]
    assert len(in_battlefield) == 1


def test_aura_falls_off_when_attached_creature_leaves():
    game_state = _build_game_state()
    creature = GameObject(
        id="aura_target",
        name="Creature",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    aura = GameObject(
        id="aura_1",
        name="Aura",
        owner_id=0,
        controller_id=0,
        types=["Enchantment", "Aura"],
        zone=ZONE_BATTLEFIELD,
        attached_to=creature.id,
    )
    game_state.add_object(creature)
    game_state.add_object(aura)

    game_state.move_object(creature.id, ZONE_GRAVEYARD)

    assert aura.zone == ZONE_GRAVEYARD
    assert aura.attached_to is None


def test_player_loses_on_zero_life():
    game_state = _build_game_state()
    player = game_state.get_player(0)
    player.life = 0

    apply_state_based_actions(game_state)

    assert player.has_lost is True


def test_draw_from_empty_library_marks_loss():
    game_state = _build_game_state()
    game_state.turn.step = Step.DRAW
    game_state.turn.phase = Phase.BEGINNING
    game_state.turn.turn_number = 2
    game_state.turn.active_player_index = 0
    player = game_state.get_player(0)
    player.library = []
    turn_manager = TurnManager(game_state)

    turn_manager._handle_draw_step()

    assert player.has_lost is True


def test_remove_player_from_game_exiles_owned_and_clears_stack():
    game_state = _build_game_state()
    owner = game_state.get_player(1)
    owned_battlefield = GameObject(
        id="owned_battlefield",
        name="Owned",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    owned_hand = GameObject(
        id="owned_hand",
        name="Owned Hand",
        owner_id=1,
        controller_id=1,
        types=["Instant"],
        zone=ZONE_HAND,
    )
    stolen = GameObject(
        id="stolen",
        name="Stolen",
        owner_id=0,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    stack_spell = GameObject(
        id="stack_spell",
        name="Stack Spell",
        owner_id=1,
        controller_id=1,
        types=["Instant"],
        zone="stack",
    )
    game_state.add_object(owned_battlefield)
    game_state.add_object(owned_hand)
    game_state.add_object(stolen)
    game_state.add_object(stack_spell)
    game_state.stack.push(
        StackItem(kind="spell", payload={"object_id": stack_spell.id, "destination_zone": ZONE_GRAVEYARD}, controller_id=1)
    )

    game_state.remove_player_from_game(1)

    assert owner.removed_from_game is True
    assert owned_battlefield.zone == ZONE_EXILE
    assert owned_hand.zone == ZONE_EXILE
    assert stack_spell.id not in [item.payload.get("object_id") for item in game_state.stack.items]
    assert stolen.controller_id == stolen.owner_id


def test_infect_damage_adds_poison_counters():
    game_state = _build_game_state()
    source = GameObject(
        id="infect_source",
        name="Infect Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
        keywords={"Infect"},
    )
    game_state.add_object(source)
    apply_damage_to_player(game_state, source, player_id=1, amount=3)

    assert game_state.get_player(1).poison_counters == 3
    assert game_state.get_player(1).life == 40


def test_infect_damage_adds_minus_counters():
    game_state = _build_game_state()
    source = GameObject(
        id="infect_source_obj",
        name="Infect Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=1,
        keywords={"Infect"},
    )
    target = GameObject(
        id="infect_target",
        name="Target",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    game_state.add_object(source)
    game_state.add_object(target)

    apply_damage_to_object(game_state, source, target, 2)
    apply_continuous_effects(game_state)

    assert target.counters.get("-1/-1") == 2
    assert target.toughness == 1


def test_poison_counters_cause_loss():
    game_state = _build_game_state()
    player = game_state.get_player(1)
    player.poison_counters = 10

    apply_state_based_actions(game_state)

    assert player.has_lost is True


def test_add_poison_effect():
    game_state = _build_game_state()
    resolver = EffectResolver(game_state)
    context = ResolveContext(controller_id=0, targets={"target_player": 1})

    result = resolver.apply({"type": "add_poison", "amount": 2, "target": "player"}, context)

    assert result["type"] == "add_poison"
    assert game_state.get_player(1).poison_counters == 2


def test_regenerate_shield_prevents_destroy():
    game_state = _build_game_state()
    creature = GameObject(
        id="regen_creature",
        name="Regen",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    creature.regenerate_shield = True
    creature.is_attacking = True
    creature.damage = 2
    game_state.add_object(creature)

    game_state.destroy_object(creature.id)

    assert creature.zone == ZONE_BATTLEFIELD
    assert creature.regenerate_shield is False
    assert creature.tapped is True
    assert creature.damage == 0
    assert creature.is_attacking is False


def test_regenerate_does_not_prevent_zero_toughness_death():
    game_state = _build_game_state()
    creature = GameObject(
        id="regen_zero",
        name="Regen Zero",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=0,
    )
    creature.regenerate_shield = True
    game_state.add_object(creature)

    apply_state_based_actions(game_state)

    assert creature.zone == ZONE_GRAVEYARD


def test_damage_to_planeswalker_removes_loyalty():
    game_state = _build_game_state()
    source = GameObject(
        id="pw_source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    planeswalker = GameObject(
        id="pw_target",
        name="Walker",
        owner_id=1,
        controller_id=1,
        types=["Planeswalker"],
        zone=ZONE_BATTLEFIELD,
    )
    planeswalker.counters["loyalty"] = 5
    game_state.add_object(source)
    game_state.add_object(planeswalker)

    apply_damage_to_object(game_state, source, planeswalker, 3)

    assert planeswalker.counters.get("loyalty") == 2
    assert planeswalker.damage == 0


def test_indestructible_survives_lethal_damage():
    game_state = _build_game_state()
    creature = GameObject(
        id="indestructible",
        name="Indestructible",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
        keywords={"Indestructible"},
    )
    creature.damage = 3
    game_state.add_object(creature)

    apply_state_based_actions(game_state)

    assert creature.zone == ZONE_BATTLEFIELD


def test_indestructible_dies_at_zero_toughness():
    game_state = _build_game_state()
    creature = GameObject(
        id="indestructible_zero",
        name="Indestructible",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=0,
        keywords={"Indestructible"},
    )
    game_state.add_object(creature)

    apply_state_based_actions(game_state)

    assert creature.zone == ZONE_GRAVEYARD


