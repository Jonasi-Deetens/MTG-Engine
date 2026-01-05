# src/axis3/rules/combat.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from axis3.state.game_state import GameState
from axis3.state.objects import RuntimeObjectId
from axis3.state.zones import ZoneType as Zone
from axis3.rules.sba import run_sbas
from axis3.rules.events import Event
from axis3.rules.layers import evaluate_characteristics

@dataclass
class CombatState:
    """
    Minimal combat representation:
    - mapping from attacker → defending player
    """
    attackers: Dict[RuntimeObjectId, int] = field(default_factory=dict)


def _get_creature_power(game_state: GameState, obj_id: RuntimeObjectId) -> int:
    """
    For now, use base power from characteristics.
    Later this will go through layers.
    """
    ec = evaluate_characteristics(game_state, obj_id)
    return ec.power

def declare_attackers(
    game_state: GameState,
    combat_state: CombatState,
    attacking_player_id: int,
    attacker_ids: List[RuntimeObjectId],
    defending_player_id: int,
) -> None:
    """
    Declare attackers. For now:
    - must be creatures
    - must be untapped
    - must not be summoning sick (no haste yet)
    - must be controlled by attacking_player_id
    """

    ps = game_state.players[attacking_player_id]

    for obj_id in attacker_ids:
        if obj_id not in ps.battlefield:
            raise ValueError(f"Object {obj_id} is not on battlefield of player {attacking_player_id}")

        rt_obj = game_state.objects[obj_id]

        if "Creature" not in rt_obj.characteristics.types:
            raise ValueError(f"Object {obj_id} is not a creature and cannot attack")

        if rt_obj.tapped:
            raise ValueError(f"Object {obj_id} is tapped and cannot attack")

        if rt_obj.summoning_sick:
            raise ValueError(f"Object {obj_id} has summoning sickness and cannot attack")

        if rt_obj.controller != attacking_player_id:
            raise ValueError(f"Object {obj_id} is not controlled by player {attacking_player_id}")

    # If all checks pass, tap them and register as attackers
    for obj_id in attacker_ids:
        rt_obj = game_state.objects[obj_id]
        rt_obj.tapped = True
        combat_state.attackers[obj_id] = defending_player_id

def perform_combat_damage(
    game_state: GameState,
    combat_state: CombatState,
) -> None:
    """
    Assign combat damage for this minimal model:
    - each attacker deals damage equal to its power to the defending player
    - no blocking, no trample, no first strike yet
    """

    for attacker_id, defending_player_id in combat_state.attackers.items():
        damage = _get_creature_power(game_state, attacker_id)
        defending_player = game_state.players[defending_player_id]
        defending_player.life -= damage

    # After damage, we'd run SBAs later (lethal damage, player death).
    # For now, we just leave life totals changed.
    run_sbas(game_state)

    game_state.event_bus.publish(Event(
        type="deals_combat_damage_to_player",
        payload={"attacker_id": attacker_id, "defending_player_id": defending_player_id}
    ))
