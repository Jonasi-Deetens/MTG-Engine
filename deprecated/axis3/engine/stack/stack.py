# src/axis3/engine/stack/stack.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Literal

from axis3.engine.stack.item import StackItem

StackItemKind = Literal["spell", "activated_ability", "triggered_ability"]

class Stack:
    """
    Axis3 stack.

    - Holds StackItem objects.
    - Does NOT contain MTG rules.
    - Delegates resolution to the casting/ability engine.
    """

    def __init__(self):
        self.items: list[StackItem] = []

    # ------------------------------------------------------------
    # Basic stack operations
    # ------------------------------------------------------------

    def push(self, item: StackItem):
        self.items.append(item)

    def pop(self) -> StackItem:
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self) -> Optional[StackItem]:
        if not self.items:
            return None
        return self.items[-1]

    def top(self) -> Optional[StackItem]:
        return self.peek()

    def is_empty(self) -> bool:
        return len(self.items) == 0

    # ------------------------------------------------------------
    # Resolution (delegated)
    # ------------------------------------------------------------

    def resolve_top(self, gs: "GameState"):
        if self.is_empty():
            return None

        item = self.pop()

        if item.is_spell():
            gs.casting.resolve_spell(gs, item.cast_context)

        elif item.is_triggered_ability():
            item.triggered_ability.resolve(gs, item.payload)

        elif item.is_activated_ability():
            item.activated_ability.resolve(gs, item.payload)

        return item
