"""
Core MTG rules layer (Comprehensive Rules / Regels).

Card text (Axis1/Axis2) describes *what a card does*.
This package enforces *when and whether* actions are legal under the game rules.
"""

from axis3.rules.core.engine import GameRulesEngine
from axis3.rules.core.catalog import RULES_CATALOG, RuleReference

__all__ = ["GameRulesEngine", "RULES_CATALOG", "RuleReference"]
