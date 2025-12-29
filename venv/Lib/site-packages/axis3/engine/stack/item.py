# axis3/rules/stack/item.py

from typing import Optional
from axis3.engine.abilities.triggered import RuntimeTriggeredAbility
from axis3.engine.abilities.activated import RuntimeActivatedAbility

class StackItem:
    """
    Represents a spell or ability on the stack.
    
    Can be:
    - A spell: obj_id + controller + optional x_value
    - A triggered ability: triggered_ability
    - An activated ability: activated_ability
    """

    def __init__(
        self,
        obj_id: Optional[str] = None,
        controller: Optional[int] = None,
        x_value: Optional[int] = None,
        triggered_ability: Optional[RuntimeTriggeredAbility] = None,
        activated_ability: Optional[RuntimeActivatedAbility] = None
    ):
        self.obj_id = obj_id
        self.controller = controller
        self.x_value = x_value
        self.triggered_ability = triggered_ability
        self.activated_ability = activated_ability

    # ------------------------
    # Helper Methods
    # ------------------------

    def is_triggered_ability(self) -> bool:
        """Returns True if this StackItem is a triggered ability."""
        return self.triggered_ability is not None

    def is_activated_ability(self) -> bool:
        """Returns True if this StackItem is an activated ability."""
        return self.activated_ability is not None

    def is_spell(self) -> bool:
        """Returns True if this StackItem is a spell (not a triggered or activated ability)."""
        return self.obj_id is not None and not self.is_triggered_ability() and not self.is_activated_ability()
