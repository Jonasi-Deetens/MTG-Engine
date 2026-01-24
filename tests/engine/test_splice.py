from engine import GameObject, GameState, PlayerState, TurnManager
from engine.rules import cast_spell
from engine.zones import ZONE_HAND


def _build_state() -> GameState:
    players = [PlayerState(id=0, life=20), PlayerState(id=1, life=20)]
    game_state = GameState(players=players)
    game_state.turn.active_player_index = 0
    game_state.turn.priority_current_index = 0
    return game_state


def test_splice_adds_effects_and_pays_cost():
    game_state = _build_state()
    spell = GameObject(
        id="arcane",
        name="Arcane Spell",
        owner_id=0,
        controller_id=0,
        types=["Instant", "Arcane"],
        zone=ZONE_HAND,
        mana_cost="{G}",
    )
    splice_card = GameObject(
        id="splice",
        name="Splice Card",
        owner_id=0,
        controller_id=0,
        types=["Instant"],
        zone=ZONE_HAND,
        mana_cost="{U}",
        effect_graphs=[],
    )
    game_state.add_object(spell)
    game_state.add_object(splice_card)
    turn_manager = TurnManager(game_state)
    player = game_state.get_player(0)
    player.mana_pool["G"] = 1

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
                        "action": {"type": "lose_life", "amount": 1, "target": "player"},
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
        context={
            "choices": {"splice_cards": [splice_card.id]},
            "targets": {"target_player": 0},
        },
    )

    assert player.life == 20

    turn_manager.handle_player_pass(0)
    turn_manager.handle_player_pass(1)

    assert player.life == 19

