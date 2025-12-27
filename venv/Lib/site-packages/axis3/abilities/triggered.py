# src/axis3/abilities/triggered.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from axis3.state.objects import RuntimeObjectId
from axis2.schema import Trigger


@dataclass
class RuntimeTriggeredAbility:
    """
    A triggered ability ready to be put on the stack.
    """
    source_id: RuntimeObjectId
    axis2_trigger: Trigger
    controller: int
