# axis3/rules/triggers/registry.py

from axis3.rules.stack.resolver import push_to_stack
from axis3.rules.triggers.runtime import RuntimeTriggeredAbility
from axis3.rules.stack.item import StackItem

# Registry keeps track of triggers to watch
_trigger_registry = []

def register_trigger(trigger):
    """
    Register a global trigger to be checked on relevant events.
    """
    _trigger_registry.append(trigger)

def check_triggers(game_state, event):
    """
    Check all triggers to see if they fire based on the given event.
    """
    # Check each object on battlefield for triggers
    for obj_id, rt_obj in game_state.objects.items():
        for trig in getattr(rt_obj.axis2, "triggers", []):
            if trig.event == event.type:
                # Fire trigger
                rta = RuntimeTriggeredAbility(
                    source_id=rt_obj.id,
                    controller=rt_obj.controller,
                    axis2_trigger=trig
                )
                # Push onto stack
                push_to_stack(game_state, StackItem(triggered_ability=rta))

    # Check global triggers
    for trig in _trigger_registry:
        if trig.event == event.type:
            rta = RuntimeTriggeredAbility(
                source_id=None,
                controller=trig.controller,
                axis2_trigger=trig
            )
            push_to_stack(game_state, StackItem(triggered_ability=rta))
