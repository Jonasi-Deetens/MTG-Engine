from engine import GameObject, GameState, PlayerState, ResolveContext, TurnManager, Phase, Step
from engine.effects.effect_resolver import EffectGraphResolver
from engine.rules import cast_spell
from engine.zones import ZONE_GRAVEYARD, ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    game_state.turn.phase = Phase.PRECOMBAT_MAIN
    game_state.turn.step = Step.PRECOMBAT_MAIN
    return game_state


def _basic_spell() -> GameObject:
    return GameObject(
        id="spell",
        name="Spell",
        owner_id=0,
        controller_id=0,
        types=["Sorcery"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )


def _spell_effect_graph() -> dict:
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
                        "action": {
                            "type": "lose_life",
                            "amount": 1,
                            "target": "player",
                        },
                    },
                },
            }
        ],
    }


def test_optional_cost_choices_do_not_set_kicker_flags():
    game_state = _build_state()
    spell = _basic_spell()
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    player.mana_pool["G"] = 2
    player.mana_pool["C"] = 1
    graph = _spell_effect_graph()

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        effect_graph=graph,
        context={
            "choices": {
                "optional_costs": {"kicker:{1}{G}": 1},
                "optional_cost_payments": [
                    {"mana_payment": {"G": 1, "C": 1}},
                ],
            }
        },
    )

    stack_item = game_state.stack.items[-1]
    choices = (stack_item.payload.get("context") or {}).get("choices") or {}
    assert choices.get("kicked") is not True
    assert choices.get("kicker_count") in (None, 0)


def test_buyback_choice_does_not_return_to_hand_without_optional_costs():
    game_state = _build_state()
    spell = _basic_spell()
    game_state.add_object(spell)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    player.mana_pool["G"] = 2
    player.mana_pool["C"] = 1
    graph = _spell_effect_graph()

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        effect_graph=graph,
        context={
            "choices": {
                "optional_costs": {"buyback:{1}{G}": 1},
                "optional_cost_payments": [
                    {"mana_payment": {"G": 1, "C": 1}},
                ],
            }
        },
    )

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert spell.zone == ZONE_GRAVEYARD


def test_kicked_condition_respects_choice():
    players = [PlayerState(id=0, life=20)]
    game_state = GameState(players=players)
    graph = {
        "id": "graph-1",
        "sourceKind": "permanent",
        "steps": [
            {
                "id": "step-1",
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
                            "type": "lose_life",
                            "amount": 3,
                            "target": "player",
                            "condition": {"type": "kicked"},
                        },
                    },
                },
            },
        ],
    }
    resolver = EffectGraphResolver(game_state)
    context = ResolveContext(controller_id=0, choices={"kicked": True}, targets={"target_player": 0})

    result = resolver.resolve(graph, context)

    assert result["step-1"]["type"] == "lose_life"
    assert game_state.get_player(0).life == 17


