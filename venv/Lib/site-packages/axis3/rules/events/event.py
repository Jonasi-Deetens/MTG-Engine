# axis3/rules/events/event.py

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Event:
    """
    A rules-level event.

    Events are:
    - immutable
    - serializable
    - replayable
    """
    type: str
    payload: Dict[str, Any]

    def __repr__(self):
        return f"<Event {self.type} {self.payload}>"
