# axis3/abilities/activated.py

class RuntimeActivatedAbility:
    """
    Represents an activated ability in the runtime.
    """
    def __init__(self, source_id: int, controller: int, cost=None, effect=None):
        self.source_id = source_id
        self.controller = controller
        self.cost = cost          # Axis2 cost object
        self.effect = effect      # Function to execute when ability resolves
        self.is_tapped_required = False
        self.once_per_turn = False
        self.has_activated_this_turn = False

    def can_activate(self, game_state):
        if self.once_per_turn and self.has_activated_this_turn:
            return False
        # TODO: Check costs (mana, tap, discard, etc.)
        return True
        
    def activate(self, game_state):
        if not self.can_activate(game_state):
            return False

        if getattr(self, "is_mana_ability", False):
            # resolve immediately
            self.effect(game_state, self.source_id, self.controller)
        else:
            # push to stack
            from axis3.rules.stack.resolver import push_to_stack
            from axis3.rules.stack.item import StackItem
            push_to_stack(game_state, StackItem(
                obj_id=self.source_id,
                controller=self.controller,
                activated_ability=self
            ))

        self.has_activated_this_turn = True
        return True
