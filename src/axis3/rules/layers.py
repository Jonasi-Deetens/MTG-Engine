# src/axis3/rules/layers.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Set

from axis3.state.game_state import GameState
from axis3.state.objects import RuntimeObjectId


@dataclass
class EvaluatedCharacteristics:
    power: int
    toughness: int
    abilities: Set[str]

def evaluate_characteristics(game_state: GameState, obj_id: RuntimeObjectId) -> EvaluatedCharacteristics:
    """
    Evaluate the current P/T and abilities of an object, applying
    continuous effects in layer order.
    """

    rt_obj = game_state.objects[obj_id]
    base = rt_obj.characteristics

    # Start from base values
    power = base.power or 0
    toughness = base.toughness or 0
    abilities: Set[str] = set()  # later: base abilities

    # LAYER 6 – abilities (grant/remove)
    for effect in game_state.continuous_effects:
        if effect.layer == 6 and effect.applies_to(game_state, obj_id):
            if effect.grant_abilities is not None:
                effect.grant_abilities(game_state, obj_id, abilities)
            if effect.remove_abilities is not None:
                effect.remove_abilities(game_state, obj_id, abilities)

    # LAYER 7b – P/T modifiers
    for effect in game_state.continuous_effects:
        if effect.layer == 7 and effect.sublayer == "7b" and effect.applies_to(game_state, obj_id):
            if effect.modify_power is not None:
                power = effect.modify_power(game_state, obj_id, power)
            if effect.modify_toughness is not None:
                toughness = effect.modify_toughness(game_state, obj_id, toughness)

    # LAYER 7c – P/T from counters
    # For now: +1/+1 counters only
    if "+1/+1" in rt_obj.counters:
        n = rt_obj.counters["+1/+1"]
        power += n
        toughness += n

    return EvaluatedCharacteristics(power=power, toughness=toughness, abilities=abilities)
