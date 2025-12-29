# axis3/abilities/activated.py

class RuntimeActivatedAbility:
    """
    Represents an activated ability in the runtime.
    """
    def __init__(self, source_id: int, controller: int, cost=None, effect=None):
        self.source_id = source_id
        self.controller = controller
        self.cost = cost
        self.effect = effect
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
            from axis3.engine.stack.item import StackItem

            game_state.stack.push(StackItem(
                obj_id=self.source_id,
                controller=int(self.controller),
                activated_ability=self
            ))

        self.has_activated_this_turn = True
        return True
