"""Core domain module - types, errors, and models."""

from .types import (
    Zone,
    EventType,
    StackItemKind,
    Phase,
    Step,
    ZONE_LIBRARY,
    ZONE_HAND,
    ZONE_BATTLEFIELD,
    ZONE_GRAVEYARD,
    ZONE_EXILE,
    ZONE_COMMAND,
    ZONE_STACK,
)
from .errors import (
    EngineError,
    InvalidTargetError,
    IllegalActionError,
    FizzleError,
    InvalidZoneError,
    ObjectNotFoundError,
    InsufficientManaError,
    ConditionNotMetError,
    ActivationLimitError,
)
from .models import (
    GameObject,
    PlayerState,
    ResolveContext,
)

__all__ = [
    # Zone enum and constants
    "Zone",
    "ZONE_LIBRARY",
    "ZONE_HAND",
    "ZONE_BATTLEFIELD",
    "ZONE_GRAVEYARD",
    "ZONE_EXILE",
    "ZONE_COMMAND",
    "ZONE_STACK",
    # Event types
    "EventType",
    # Stack item kinds
    "StackItemKind",
    # Phase and step
    "Phase",
    "Step",
    # Errors
    "EngineError",
    "InvalidTargetError",
    "IllegalActionError",
    "FizzleError",
    "InvalidZoneError",
    "ObjectNotFoundError",
    "InsufficientManaError",
    "ConditionNotMetError",
    "ActivationLimitError",
    # Models
    "GameObject",
    "PlayerState",
    "ResolveContext",
]
