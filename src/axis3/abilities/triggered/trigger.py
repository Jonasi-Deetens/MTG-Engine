# axis3/engine/abilities/triggered/trigger.py

from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Trigger:
    """
    Axis3 trigger definition.

    A trigger consists of:
      - event: the event type string (e.g. "enter_battlefield", "dies", "attacks")
      - condition: optional condition object that must evaluate to True
      - effect: an Axis3Effect instance to apply when triggered
      - mandatory: whether the trigger must fire (default True)
      - targeting_rules: optional targeting rules for the effect
    """

    event: str
    condition: Optional[Any]
    effect: Any
    mandatory: bool = True
    targeting_rules: Optional[Any] = None
