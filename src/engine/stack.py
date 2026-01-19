from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional


StackItemKind = Literal["spell", "activated_ability", "triggered_ability", "ability_graph"]


@dataclass
class StackItem:
    kind: StackItemKind
    payload: Dict[str, Any] = field(default_factory=dict)
    controller_id: Optional[int] = None


class Stack:
    def __init__(self) -> None:
        self.items: list[StackItem] = []

    def push(self, item: StackItem) -> None:
        self.items.append(item)

    def pop(self) -> StackItem:
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self) -> Optional[StackItem]:
        if not self.items:
            return None
        return self.items[-1]

    def is_empty(self) -> bool:
        return len(self.items) == 0
