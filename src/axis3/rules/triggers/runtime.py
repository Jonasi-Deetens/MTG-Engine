# axis3/rules/triggers/runtime.py

from axis3.rules.stack.item import StackItem

class RuntimeTriggeredAbility:
    """
    Represents a triggered ability in the runtime.
    """
    def __init__(self, source_id: int, controller: int, axis2_trigger):
        self.source_id = source_id
        self.controller = controller
        self.axis2_trigger = axis2_trigger  # Original Axis2 trigger object

def resolve_runtime_triggered_ability(game_state: "GameState", rta: RuntimeTriggeredAbility):
    """
    Resolve a triggered ability immediately (Phase 2 simplification).
    Executes the effect_text in Axis2 trigger.
    """
    from axis3.rules.stack.resolver import push_to_stack
    effect = rta.axis2_trigger.effect_text.lower()
    
    # Example effect parsing (stub, extend later)
    if "draw a card" in effect:
        from axis3.rules.atomic.draw import apply_draw
        apply_draw(game_state, rta.controller, 1)

    if "lose 1 life" in effect:
        from axis3.rules.atomic.life import apply_life_change
        apply_life_change(game_state, rta.controller, -1)

    # TODO: parse full effect text and execute other actions
