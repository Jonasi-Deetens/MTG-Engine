# src/axis3/translate/ability_builder.py

from __future__ import annotations
from typing import List

from axis3.abilities.triggered import RuntimeTriggeredAbility
from axis3.abilities.activated import RuntimeActivatedAbility
from axis3.abilities.static import RuntimeContinuousEffect
from axis3.state.objects import RuntimeObject
from axis3.rules.events import Event
from axis3.engine.stack.item import StackItem
from axis3.state.game_state import GameState


def register_runtime_abilities_for_object(game_state: GameState, rt_obj: RuntimeObject):
    """
    Build all runtime ability objects from Axis2 and attach to the runtime object.
    This includes:
    - Triggered abilities (go on stack via event bus)
    - Activated abilities (stored on the object)
    - Static / continuous effects (stored on the object for layers)
    """

    # --------------------------
    # 1. Triggered abilities
    # --------------------------
    for trig in getattr(rt_obj.axis2_card, "triggers", []):
        event_type = trig.event  # e.g., "enters_battlefield", "dies"

        def make_callback(trig=trig, source_id=rt_obj.id):
            def callback(event: Event):
                rta = RuntimeTriggeredAbility(
                    source_id=source_id,
                    axis2_trigger=trig,
                    controller=rt_obj.controller,
                )

                stack_item = StackItem(
                    obj_id=source_id,
                    controller=rt_obj.controller,
                    x_value=None,
                    triggered_ability=rta
                )

                game_state.stack.push(stack_item)
            return callback

        game_state.event_bus.subscribe(event_type, make_callback())

    # --------------------------
    # 2. Activated abilities
    # --------------------------
    rt_obj.activated_abilities = []
    for act in getattr(rt_obj.axis2_card, "activated_abilities", []):
        raa = RuntimeActivatedAbility(
            source_id=rt_obj.id,
            axis2_ability=act,
            controller=rt_obj.controller,
        )
        rt_obj.activated_abilities.append(raa)

    # --------------------------
    # 3. Static / continuous effects
    # --------------------------
    rt_obj.static_abilities = []
    for eff in getattr(rt_obj.axis2_card, "static_effects", []):
        rce = RuntimeContinuousEffect(
            source_id=rt_obj.id,
            layer=eff.layer,
            sublayer=getattr(eff, "sublayer", None),
            applies_to=lambda gs, obj_id: True,  # simplistic: can refine later
            modify_power=getattr(eff, "modify_power", None),
            modify_toughness=getattr(eff, "modify_toughness", None),
            grant_abilities=getattr(eff, "grant_abilities", None),
            remove_abilities=getattr(eff, "remove_abilities", None),
        )
        rt_obj.static_abilities.append(rce)
