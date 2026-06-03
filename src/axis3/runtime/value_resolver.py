from __future__ import annotations

from typing import Any, Optional, Union

from axis2.schema import SymbolicValue, DynamicValue


def resolve_amount(
    value: Union[int, str, SymbolicValue, DynamicValue, None],
    *,
    game_state: Any = None,
    source_id: Optional[str] = None,
    controller: Optional[int] = None,
    default: int = 0,
) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
        return default
    if isinstance(value, SymbolicValue):
        if value.kind == "variable":
            # X and similar — caller should pass via game state when available
            x = getattr(game_state, "chosen_x", None) if game_state else None
            return int(x) if x is not None else default
        if value.kind == "star":
            return 0
        return default
    if isinstance(value, DynamicValue):
        if value.kind == "counter_count" and game_state and source_id:
            obj = game_state.get_object(source_id)
            if obj and value.counter_type:
                return obj.counters.get(value.counter_type, 0)
        return default
    return default
