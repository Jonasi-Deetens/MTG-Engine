# axis3/engine/casting/context.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CastContext:
    """
    Represents the full context of a spell being cast.

    This object is created at the start of the casting pipeline and
    passed through permission checks, cost building, cost payment,
    replacement effects, and finally resolution.

    It is also used by replacement effects to determine whether
    certain conditions apply (e.g., "if this spell was cast via flashback").
    """

    source_id: str
    controller: int
    origin_zone: str

    # The final mana cost chosen by the player (after reductions)
    chosen_cost: Optional[str] = None

    # The tag of the alternative cost used, if any (e.g., "flashback", "escape")
    used_alt_cost: Optional[str] = None

    # Additional costs paid (e.g., kicker, casualty, exploit)
    additional_costs_paid: Dict[str, Any] = field(default_factory=dict)

    # Cost reductions applied (for debugging and UI)
    reductions_applied: List[Dict[str, Any]] = field(default_factory=list)

    # Whether the cast was legal
    legal: bool = True

    # Metadata for replacement effects
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Whether the spell has been placed on the stack
    placed_on_stack: bool = False

    # Whether the spell has resolved
    resolved: bool = False

    # Whether the spell was countered
    countered: bool = False

    # ============================================================
    # Helper methods
    # ============================================================

    def mark_alt_cost_used(self, tag: str):
        """Record that an alternative cost was chosen."""
        self.used_alt_cost = tag

    def used_alternative_cost(self, tag: str) -> bool:
        """Check if a specific alternative cost was used."""
        return self.used_alt_cost == tag

    def add_reduction(self, tag: str, amount: int):
        """Record a cost reduction for debugging/UI."""
        self.reductions_applied.append({"tag": tag, "amount": amount})

    def add_additional_cost(self, tag: str, value: Any):
        """Record an additional cost paid."""
        self.additional_costs_paid[tag] = value

    def set_chosen_cost(self, cost: str):
        """Set the final mana cost after reductions."""
        self.chosen_cost = cost

    def set_illegal(self, reason: str):
        """Mark the cast as illegal and store the reason."""
        self.legal = False
        self.metadata["illegal_reason"] = reason

    def add_metadata(self, key: str, value: Any):
        """Store arbitrary metadata for replacement effects."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default=None):
        return self.metadata.get(key, default)
