from api.routes.engine import _build_game_state
from api.schemas.engine_schemas import GameStateSnapshot


def test_build_game_state_filters_missing_ids():
    snapshot = GameStateSnapshot(
        players=[
            {
                "id": 1,
                "life": 40,
                "mana_pool": {},
                "library": ["obj_1", "missing_obj"],
                "hand": [],
                "graveyard": [],
                "exile": [],
                "command": [],
                "battlefield": [],
                "commander_id": None,
                "commander_tax": 0,
                "commander_damage_taken": {},
            }
        ],
        objects=[
            {
                "id": "obj_1",
                "name": "Test Card",
                "owner_id": 1,
                "controller_id": 1,
                "types": ["Creature"],
                "zone": "library",
                "mana_cost": None,
                "mana_value": 1,
                "power": 1,
                "toughness": 1,
                "tapped": False,
                "damage": 0,
                "counters": {},
                "keywords": [],
                "protections": [],
                "is_token": False,
                "was_cast": False,
                "is_attacking": False,
                "is_blocking": False,
                "phased_out": False,
                "transformed": False,
                "regenerate_shield": False,
                "effect_graphs": [],
                "base_effect_graphs": [],
                "temporary_effects": [],
                "activation_limits": {},
                "etb_choices": {},
                "base_etb_choices": {},
            }
        ],
        stack=[],
        turn={
            "turn_number": 1,
            "active_player_index": 0,
            "phase": "beginning",
            "step": "untap",
            "land_plays_this_turn": 0,
            "combat_state": None,
            "priority_current_index": 0,
            "priority_pass_count": 0,
            "priority_last_passed_player_id": None,
        },
        debug_log=[],
    )

    game_state = _build_game_state(snapshot)
    player = game_state.get_player(1)
    assert player.library == ["obj_1"]
