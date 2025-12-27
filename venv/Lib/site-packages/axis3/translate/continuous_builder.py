# src/axis3/translate/continuous_builder.py

from __future__ import annotations

from typing import List

from axis3.abilities.static import RuntimeContinuousEffect
from axis3.state.game_state import GameState
from axis3.state.objects import RuntimeObject
from axis3.state.zones import ZoneType as Zone


def build_continuous_effects_for_object(game_state: GameState, rt_obj: RuntimeObject):
    """
    Translate Axis2 continuous effects on this object into RuntimeContinuousEffect
    and append them to game_state.continuous_effects.
    """

    axis2 = rt_obj.axis2

    for ce in axis2.continuous_effects:
        kind = ce.kind  # This depends on your Axis2 schema

        # Example 1: global anthem: "Creatures you control get +1/+1"
        if kind == "global_pt_modifier":
            amount_power = ce.value.get("power", 0)
            amount_toughness = ce.value.get("toughness", 0)

            def applies_to(gs, obj_id, controller=rt_obj.controller):
                obj = gs.objects[obj_id]
                return (
                    obj.zone == Zone.BATTLEFIELD
                    and obj.controller == controller
                    and "Creature" in obj.characteristics.types
                )

            def mod_p(gs, obj_id, current, dp=amount_power):
                return current + dp

            def mod_t(gs, obj_id, current, dt=amount_toughness):
                return current + dt

            game_state.continuous_effects.append(
                RuntimeContinuousEffect(
                    source_id=rt_obj.id,
                    layer=7,
                    sublayer="7b",
                    applies_to=applies_to,
                    modify_power=mod_p,
                    modify_toughness=mod_t,
                )
            )

        # Example 2: “Enchanted creature gets +2/+2 and has flying”
        # You’d have ce.targeting / aura metadata; we simplify:
        if kind == "aura_pt_and_ability":
            amount_power = ce.value.get("power", 0)
            amount_toughness = ce.value.get("toughness", 0)
            abilities = set(ce.value.get("abilities", []))  # e.g. {"flying"}

            def applies_to(gs, obj_id, source_id=rt_obj.id):
                # Assume rt_obj is the Aura; it must be attached_to something
                aura = gs.objects[source_id]
                return aura.attached_to == obj_id and gs.objects[obj_id].zone == Zone.BATTLEFIELD

            def mod_p(gs, obj_id, current, dp=amount_power):
                return current + dp

            def mod_t(gs, obj_id, current, dt=amount_toughness):
                return current + dt

            def grant_abil(gs, obj_id, ability_set, new_abilities=abilities):
                ability_set.update(new_abilities)

            # Layer 6 – grant abilities
            game_state.continuous_effects.append(
                RuntimeContinuousEffect(
                    source_id=rt_obj.id,
                    layer=6,
                    sublayer=None,
                    applies_to=applies_to,
                    grant_abilities=grant_abil,
                )
            )

            # Layer 7b – modify P/T
            game_state.continuous_effects.append(
                RuntimeContinuousEffect(
                    source_id=rt_obj.id,
                    layer=7,
                    sublayer="7b",
                    applies_to=applies_to,
                    modify_power=mod_p,
                    modify_toughness=mod_t,
                )
            )
