"""Canonical Axis1 → Axis2 → runtime integration (use instead of legacy builders)."""

from axis3.integration.runtime_loader import (
    compile_axis2,
    create_runtime_object,
    build_game_state_from_axis1_decks,
)

__all__ = [
    "compile_axis2",
    "create_runtime_object",
    "build_game_state_from_axis1_decks",
]
