from __future__ import annotations

import copy
from typing import Any, Dict, Iterable, Optional

from .stack import StackItem
from .state import GameState


def push_spell_copies(
    game_state: GameState,
    source_id: str,
    effect_graph: Optional[dict],
    base_context: Dict[str, Any],
    controller_id: int,
    count: int,
    copy_targets_list: Optional[Iterable[Dict[str, Any]]] = None,
) -> None:
    overrides = list(copy_targets_list or [])
    for index in range(count):
        context = copy.deepcopy(base_context or {})
        if index < len(overrides) and isinstance(overrides[index], dict):
            context.update(overrides[index])
        if effect_graph:
            payload = {
                "graph": effect_graph,
                "context": context,
                "copy_of": source_id,
                "is_copy": True,
                "source_object_id": None,
                "destination_zone": None,
            }
            game_state.stack.push(StackItem(kind="effect_graph", payload=payload, controller_id=controller_id))
        else:
            payload = {
                "context": context,
                "copy_of": source_id,
                "is_copy": True,
                "destination_zone": None,
            }
            game_state.stack.push(StackItem(kind="spell", payload=payload, controller_id=controller_id))

