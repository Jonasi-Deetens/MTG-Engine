from dataclasses import dataclass
from typing import List, Dict, Any

from axis2.schema import TargetingRules

@dataclass
class ContinuousEffect:
    """
    Represents a continuous effect (Layer 4–7, rule modifications, etc.)
    """
    kind: str
    subject: str
    value: Dict[str, Any]
    layering: str
