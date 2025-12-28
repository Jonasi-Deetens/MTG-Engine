# axis3/rules/stack/item.py

from typing import Optional
from axis3.abilities.triggered import RuntimeTriggeredAbility

class StackItem:
    """
    Represents a spell or ability on the stack.
    """
    def __init__(self,
                 obj_id: Optional[int] = None,
                 controller: Optional[int] = None,
                 x_value: Optional[int] = None,
                 triggered_ability: Optional[RuntimeTriggeredAbility] = None):
        self.obj_id = obj_id
        self.controller = controller
        self.x_value = x_value
        self.triggered_ability = triggered_ability

    def is_triggered_ability(self) -> bool:
        return self.triggered_ability is not None
