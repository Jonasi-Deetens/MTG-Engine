from engine import CombatState, GameObject, GameState, PlayerState
from engine.combat_damage import resolve_combat_damage
from engine.damage import apply_damage_to_player
from engine.zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD


class _DummyTurnManager:
    def after_player_action(self, player_id: int) -> None:
        return


def _build_state() -> GameState:
    players = [PlayerState(id=0), PlayerState(id=1)]
    return GameState(players=players)


def _trigger_graph(scope: str = "any") -> dict:
    return {
        "id": "graph-1",
        "sourceKind": "permanent",
        "steps": [
            {
                "id": "step-1",
                "effect": {
                    "id": "eff-1",
                    "initiation": "triggered",
                    "resolution": "stack",
                    "persistence": "instant",
                    "tags": [],
                    "trigger": {"event": "dies", "scope": scope},
                    "effect": {
                        "kind": "one_shot",
                        "action": {"type": "life", "amount": 0},
                    },
                },
            },
        ],
    }

def test_blocker_order_choice_queued():
    game_state = _build_state()
    attacker = GameObject(
        id="attacker",
        name="Attacker",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    attacker.is_attacking = True
    b1 = GameObject(
        id="b1",
        name="Blocker 1",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=2,
    )
    b1.is_blocking = True
    b2 = GameObject(
        id="b2",
        name="Blocker 2",
        owner_id=1,
        controller_id=1,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=1,
        toughness=2,
    )
    b2.is_blocking = True
    game_state.add_object(attacker)
    game_state.add_object(b1)
    game_state.add_object(b2)
    game_state.turn.combat_state = CombatState(
        attacking_player_id=0,
        defending_player_id=1,
        attackers=[attacker.id],
        blockers={attacker.id: [b1.id, b2.id]},
    )

    resolve_combat_damage(game_state, _DummyTurnManager(), player_id=0)

    pending = game_state.choices.get("pending", [])
    assert any(entry.get("type") == "blocker_order" and entry.get("player_id") == 0 for entry in pending)


def test_zone_replacement_choice_queued_with_player_id():
    game_state = _build_state()
    obj = GameObject(
        id="obj",
        name="Obj",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=2,
        toughness=2,
    )
    obj.temporary_effects.append({
        "type": "replace_zone_change",
        "from_zone": ZONE_BATTLEFIELD,
        "to_zone": ZONE_GRAVEYARD,
        "replacement_zone": "exile",
        "effect_id": "t1",
        "timestamp_order": 1,
    })
    game_state.replacement_effects.append({
        "type": "replace_zone_change",
        "from_zone": ZONE_BATTLEFIELD,
        "to_zone": ZONE_GRAVEYARD,
        "replacement_zone": "hand",
        "effect_id": "t2",
        "timestamp_order": 2,
    })
    game_state.add_object(obj)

    game_state.move_object(obj.id, ZONE_GRAVEYARD)

    pending = game_state.choices.get("pending", [])
    assert any(entry.get("type") == "zone_replacement" and entry.get("player_id") == 0 for entry in pending)


def test_damage_replacement_choice_queued_with_player_id():
    game_state = _build_state()
    source = GameObject(
        id="source",
        name="Source",
        owner_id=0,
        controller_id=0,
        types=["Creature"],
        zone=ZONE_BATTLEFIELD,
        power=3,
        toughness=3,
    )
    game_state.add_object(source)
    game_state.replacement_effects.append({
        "type": "redirect_damage",
        "source": source.id,
        "redirect_player_id": 0,
        "amount": 3,
        "effect_id": "r1",
        "timestamp_order": 1,
    })
    game_state.replacement_effects.append({
        "type": "prevent_damage",
        "player_id": 1,
        "amount": 3,
        "effect_id": "p1",
        "timestamp_order": 2,
    })

    apply_damage_to_player(game_state, source, 1, 3)

    pending = game_state.choices.get("pending", [])
    assert any(entry.get("type") == "damage_replacement" and entry.get("player_id") == 1 for entry in pending)

