from __future__ import annotations

from typing import Any, Dict, Optional

from api.schemas.unified_effect_schemas import EffectGraph, UnifiedEffect
from .active_effects import ActiveEffect
from .normalize import normalize_graph
from ..effects_internal.effect_router import create_default_router
from ..choices import validate_modal_choices_effect_graph
from ..state import GameState, ResolveContext


class EffectGraphResolver:
    def __init__(self, game_state: GameState) -> None:
        self._gs = game_state
        self._router = create_default_router(game_state)

    def resolve(
        self,
        graph: EffectGraph | Dict[str, Any],
        context: ResolveContext,
        start_step_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized = normalize_graph(graph)
        validate_modal_choices_effect_graph(
            normalized.model_dump(by_alias=True),
            context.__dict__,
        )
        steps_by_id = {step.id: step for step in normalized.steps}
        if not steps_by_id:
            return {}

        current_id = start_step_id or normalized.steps[0].id
        results: Dict[str, Any] = {}

        while current_id:
            step = steps_by_id.get(current_id)
            if not step:
                break
            result = self._resolve_effect(step, context)
            results[step.id] = result
            current_id = self._next_step_id(step, context)

        return results

    def _resolve_effect(self, step, context: ResolveContext) -> Dict[str, Any]:
        effect = step.effect
        body = effect.effect
        kind = getattr(body, "kind", None)

        if kind == "one_shot":
            payload = _model_dump(body.action)
            payload.setdefault("type", getattr(body.action, "type", None))
            payload["_node_id"] = step.id
            return self._router.apply(payload, context)

        if kind in ("continuous", "replacement", "prevention"):
            if not self._should_register_continuous(body):
                return {"type": kind, "status": "skipped", "reason": "unsupported_duration"}

            active = ActiveEffect(
                effect_id=effect.id,
                source_id=context.source_id or "",
                controller_id=context.controller_id or 0,
                effect_data=effect,
                timestamp=self._gs.turn.turn_number,
                timestamp_order=self._next_effect_order(),
                effect_graph=None,
                step_id=None,
            )
            self._gs.active_effect_registry.register(active)
            return {"type": kind, "status": "registered"}

        return {"type": str(kind), "status": "unhandled"}

    def _should_register_continuous(self, body: Any) -> bool:
        if getattr(body, "kind", None) != "continuous":
            return True
        duration = getattr(body, "duration", None)
        duration_type = getattr(duration, "type", None) if duration else None
        return duration_type == "while_in_zone"

    @staticmethod
    def _next_step_id(step, context: ResolveContext) -> Optional[str]:
        choices = getattr(context, "choices", None)
        selected_modes = []
        if isinstance(choices, dict):
            raw = choices.get("chosen_modes") or choices.get("chosen_mode")
            if isinstance(raw, list):
                selected_modes = [m for m in raw if isinstance(m, str)]
            elif isinstance(raw, str):
                selected_modes = [raw]

        if selected_modes:
            next_by_mode = getattr(step, "nextByMode", None)
            if isinstance(next_by_mode, dict):
                for mode_id in selected_modes:
                    next_step = next_by_mode.get(mode_id)
                    if next_step:
                        return next_step

        next_steps = getattr(step, "next", None)
        if isinstance(next_steps, list) and next_steps:
            return next_steps[0]
        return None

    def _next_effect_order(self) -> int:
        self._gs.effect_timestamp_counter += 1
        return self._gs.effect_timestamp_counter


def _model_dump(value: Any) -> Dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True)
    if isinstance(value, dict):
        return dict(value)
    return {}
