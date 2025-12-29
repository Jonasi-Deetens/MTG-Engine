# axis3/effects/base.py 
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable

class Effect: 
    def apply(self, gs, source, **kwargs): 
        raise NotImplementedError

@dataclass 
class ReplacementEffect: 
    event: str 
    replace_with: Effect 
    condition: Optional[Callable] = None

@dataclass 
class ContinuousEffect: 
    effect_type: str 
    selector: Callable 
    params: dict

@dataclass
class StaticEffect:
    """
    Represents static continuous effects, including type-changing effects.
    Applies in the specified zones and participates in layer processing.
    """
    kind: str                     # e.g. "type_changer", "buff", "restriction"
    subject: str                  # "this", "creatures_you_control", etc.
    value: Dict[str, Any]         # effect-specific payload
    layering: str                 # e.g. "layer_4", "layer_7b"
    zones: List[str] = None       # ["battlefield"], ["all"], ["hand","graveyard"], etc.
