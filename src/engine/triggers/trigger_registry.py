"""Deprecated trigger registry retained for compatibility."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Set


@dataclass
class RegisteredTrigger:
    source_id: str
    controller_id: int
    trigger: str
    graph: Dict[str, Any]
    trigger_data: Dict[str, Any] | None
    index: int = 0


class TriggerRegistry:
    """No-op registry for legacy trigger graphs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._registered: List[RegisteredTrigger] = []

    @property
    def registered(self) -> List[RegisteredTrigger]:
        return []

    @property
    def registered_triggers(self) -> Set[str]:
        return set()

    def register_from_objects(self, *args: Any, **kwargs: Any) -> None:
        return

    def register_object(self, *args: Any, **kwargs: Any) -> None:
        return

    def unregister_object(self, *args: Any, **kwargs: Any) -> None:
        return
