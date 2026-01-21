"""Custom exception hierarchy for the MTG engine."""

from __future__ import annotations

from typing import Any, Optional


class EngineError(Exception):
    """Base exception for all engine errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidTargetError(EngineError):
    """Raised when a target is invalid or illegal."""

    def __init__(
        self,
        message: str = "Invalid target",
        target_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        details = {}
        if target_id:
            details["target_id"] = target_id
        if reason:
            details["reason"] = reason
        super().__init__(message, details)
        self.target_id = target_id
        self.reason = reason


class IllegalActionError(EngineError):
    """Raised when an action cannot be legally performed."""

    def __init__(
        self,
        message: str = "Illegal action",
        action: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        details = {}
        if action:
            details["action"] = action
        if reason:
            details["reason"] = reason
        super().__init__(message, details)
        self.action = action
        self.reason = reason


class FizzleError(EngineError):
    """Raised when a spell or ability fizzles due to all targets being illegal."""

    def __init__(
        self,
        message: str = "Spell or ability fizzled",
        source_id: Optional[str] = None,
    ) -> None:
        details = {}
        if source_id:
            details["source_id"] = source_id
        super().__init__(message, details)
        self.source_id = source_id


class InvalidZoneError(EngineError):
    """Raised when an object is in an unexpected zone."""

    def __init__(
        self,
        message: str = "Invalid zone",
        object_id: Optional[str] = None,
        expected_zone: Optional[str] = None,
        actual_zone: Optional[str] = None,
    ) -> None:
        details = {}
        if object_id:
            details["object_id"] = object_id
        if expected_zone:
            details["expected_zone"] = expected_zone
        if actual_zone:
            details["actual_zone"] = actual_zone
        super().__init__(message, details)
        self.object_id = object_id
        self.expected_zone = expected_zone
        self.actual_zone = actual_zone


class ObjectNotFoundError(EngineError):
    """Raised when a game object cannot be found."""

    def __init__(
        self,
        message: str = "Object not found",
        object_id: Optional[str] = None,
    ) -> None:
        details = {}
        if object_id:
            details["object_id"] = object_id
        super().__init__(message, details)
        self.object_id = object_id


class InsufficientManaError(EngineError):
    """Raised when a player doesn't have enough mana."""

    def __init__(
        self,
        message: str = "Insufficient mana",
        required: Optional[dict[str, int]] = None,
        available: Optional[dict[str, int]] = None,
    ) -> None:
        details = {}
        if required:
            details["required"] = required
        if available:
            details["available"] = available
        super().__init__(message, details)
        self.required = required
        self.available = available


class ConditionNotMetError(EngineError):
    """Raised when a condition for an ability or effect is not met."""

    def __init__(
        self,
        message: str = "Condition not met",
        condition_type: Optional[str] = None,
    ) -> None:
        details = {}
        if condition_type:
            details["condition_type"] = condition_type
        super().__init__(message, details)
        self.condition_type = condition_type


class ActivationLimitError(EngineError):
    """Raised when an ability's activation limit has been reached."""

    def __init__(
        self,
        message: str = "Activation limit reached",
        ability_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> None:
        details = {}
        if ability_id:
            details["ability_id"] = ability_id
        if limit is not None:
            details["limit"] = limit
        super().__init__(message, details)
        self.ability_id = ability_id
        self.limit = limit
