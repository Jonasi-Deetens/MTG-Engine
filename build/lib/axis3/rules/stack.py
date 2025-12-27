# src/axis3/rules/stack.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from axis3.state.objects import RuntimeObjectId

@dataclass
class StackItem:
    """
    Represents either:
    - a spell on the stack (obj_id, controller, x_value)
    - a triggered ability (triggered_ability)
    """
    obj_id: Optional[str] = None
    controller: Optional[int] = None
    x_value: Optional[int] = None
    triggered_ability: Optional["RuntimeTriggeredAbility"] = None

class Stack:
    """
    LIFO stack for spells and abilities.
    """

    def __init__(self):
        self.items: list[StackItem] = []

    def push(self, item: StackItem):
        self.items.append(item)

    def pop(self) -> StackItem:
        return self.items.pop()

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return f"Stack({self.items})"
