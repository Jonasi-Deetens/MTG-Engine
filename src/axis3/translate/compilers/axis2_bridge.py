"""Bridge legacy text compilation to Axis2 structured execution."""

from __future__ import annotations

from typing import Any, List

from axis2 import schema as a2


def execute_effects(
    game_state: Any,
    effects: List[a2.Effect],
    source_id: str,
    controller: int,
) -> None:
    game_state.effect_executor.execute_all(effects, source_id, controller)


def compile_and_execute_text(
    game_state: Any,
    effect_text: str,
    source_id: str,
    controller: int,
):
    """
    Fallback: parse a single line with Axis2 effect dispatcher when possible.
    """
    from axis2.parsing.effects.dispatcher import parse_effect_text
    from axis2.schema import ParseContext

    ctx = ParseContext(
        card_name="runtime",
        primary_type="Instant",
        face_name="runtime",
        face_types=["Instant"],
        is_spell_text=True,
    )
    parsed = parse_effect_text(effect_text, ctx)
    if parsed:
        execute_effects(game_state, parsed, source_id, controller)
    else:
        game_state.add_debug_log(f"[axis2_bridge] unparsed: {effect_text[:80]}")
