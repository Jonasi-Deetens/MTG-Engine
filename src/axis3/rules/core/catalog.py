from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RuleReference:
    """Maps a Comprehensive Rules section to engine code."""

    cr_section: str
    title: str
    module: str
    implemented: bool = True
    notes: str = ""


# Curated map for the rules we implement or partially implement.
RULES_CATALOG: List[RuleReference] = [
    RuleReference("100", "Game Concepts", "axis3.rules.core.engine", True),
    RuleReference("117", "Timing and Priority", "axis3.engine.turn.priority", True),
    RuleReference("118", "Costs", "axis3.runtime.cost_executor", True, "Activated costs"),
    RuleReference("305", "Lands", "axis3.rules.core.permissions", True, "One land per turn"),
    RuleReference("400", "Zones", "axis3.engine.movement.zone_movement", True),
    RuleReference("405", "Stack", "axis3.engine.stack", True),
    RuleReference("601", "Casting Spells", "axis3.engine.casting", True, "Partial"),
    RuleReference("608", "Resolving Spells", "axis3.engine.stack.resolver", True, "Partial"),
    RuleReference("704", "State-Based Actions", "axis3.rules.sba", True, "Partial"),
    RuleReference("613", "Interaction of Continuous Effects", "axis3.rules.layers", False, "Scaffold"),
    RuleReference("506", "Combat Phase", "axis3.engine.combat", False, "Stub"),
]
