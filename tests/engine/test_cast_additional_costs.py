from engine import GameObject, GameState, PlayerState, TurnManager, Phase, Step
from engine.rules import cast_spell
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND


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


def test_additional_cast_cost_discard_required():
    game_state = _build_state()
    spell = _basic_spell()
    discard = GameObject(
        id="discard",
        name="Discard",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
    )
    game_state.add_object(spell)
    game_state.add_object(discard)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1
    graph = {
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
                        "action": {"type": "life", "amount": 0},
                    },
                },
            }
        ],
    }

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        effect_graph=graph,
        context={"choices": {}},
    )

    assert discard.zone == ZONE_HAND


def test_additional_cast_cost_sacrifice():
    game_state = _build_state()
    spell = _basic_spell()
    spell.id = "spell_two"
    sacrifice = GameObject(
        id="fodder",
        name="Fodder",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
    )
    game_state.add_object(spell)
    game_state.add_object(sacrifice)
    turn_manager = TurnManager(game_state)
    game_state.get_player(0).mana_pool["G"] = 1
    graph = {
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
                        "action": {"type": "life", "amount": 0},
                    },
                },
            }
        ],
    }

    cast_spell(
        game_state,
        turn_manager,
        player_id=0,
        object_id=spell.id,
        effect_graph=graph,
        context={"choices": {"additional_cost_payments": {spell.id: {"sacrifice_id": sacrifice.id}}}},
    )

    assert sacrifice.zone == ZONE_BATTLEFIELD

