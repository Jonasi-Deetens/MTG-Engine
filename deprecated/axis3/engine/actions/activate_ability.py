from .base import Action
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.engine.stack.item import StackItem

class ActivateAbilityAction(Action):
    def __init__(self, player_id, obj_id, ability_index, uses_priority=True):
        self.player_id = player_id
        self.obj_id = obj_id
        self.ability_index = ability_index
        self.uses_priority = uses_priority

    def execute(self, game_state):
        obj = game_state.get_object(self.obj_id)
        ability = obj.activated_abilities[self.ability_index]

        # -----------------------------------------
        # 1. MANA ABILITIES (resolve immediately)
        # -----------------------------------------
        if ability.is_mana_ability:
            self.uses_priority = False 
            # Pay costs
            for cost in ability.cost:
                cost.pay(game_state, obj)

            # Apply effects
            for eff in ability.effect:
                eff.apply(game_state, obj)

            # Fire event for triggers
            game_state.event_bus.publish(Event(
                type=EventType.MANA_ABILITY_RESOLVED,
                payload={
                    "obj_id": obj.id,
                    "controller": obj.controller
                }
            ))

            return  # no stack, no priority pass

        self.uses_priority = True
        # -----------------------------------------
        # 2. NON-MANA ACTIVATED ABILITIES
        # -----------------------------------------
        # Pay costs
        for cost in ability.cost:
            cost.pay(game_state, obj)

        # Put ability on stack
        stack_item = StackItem(
            obj_id=obj.id,
            controller=obj.controller,
            activated_ability=ability
        )
        game_state.stack.push(stack_item)

        # Fire event for triggers
        game_state.event_bus.publish(Event(
            type=EventType.ACTIVATED_ABILITY,
            payload={
                "obj_id": obj.id,
                "controller": obj.controller
            }
        ))

        game_state.event_bus.publish(Event(
            type=EventType.PUT_ON_STACK,
            payload={
                "obj_id": obj.id,
                "controller": obj.controller
            }
        ))
