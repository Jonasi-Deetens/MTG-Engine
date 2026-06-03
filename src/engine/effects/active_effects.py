from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from api.schemas.unified_effect_schemas import EffectGraph, UnifiedEffect


@dataclass
class ActiveEffect:
    effect_id: str
    source_id: str
    controller_id: int
    effect_data: UnifiedEffect
    timestamp: int
    timestamp_order: int
    effect_graph: Optional[EffectGraph] = None
    step_id: Optional[str] = None


class ActiveEffectRegistry:
    def __init__(self) -> None:
        self.effects: List[ActiveEffect] = []
        self._by_source: Dict[str, List[ActiveEffect]] = {}
        self._by_trigger_event: Dict[str, List[ActiveEffect]] = {}
        self._by_replacement_event: Dict[str, List[ActiveEffect]] = {}
        self._by_layer: Dict[int, List[ActiveEffect]] = {}

    def register(self, effect: ActiveEffect) -> None:
        self.effects.append(effect)
        self._by_source.setdefault(effect.source_id, []).append(effect)

        trigger_event = self._extract_trigger_event(effect)
        if trigger_event:
            self._by_trigger_event.setdefault(trigger_event, []).append(effect)

        replacement_event = self._extract_replacement_event(effect)
        if replacement_event:
            self._by_replacement_event.setdefault(replacement_event, []).append(effect)

        layer = self._extract_continuous_layer(effect)
        if layer is not None:
            self._by_layer.setdefault(layer, []).append(effect)

    def unregister_by_source(self, source_id: str) -> None:
        effects = self._by_source.pop(source_id, [])
        for effect in effects:
            if effect in self.effects:
                self.effects.remove(effect)
            self._remove_from_indices(effect)

    def get_triggered_for_event(self, event: str) -> List[ActiveEffect]:
        return list(self._by_trigger_event.get(event, []))

    def get_trigger_event_types(self) -> List[str]:
        return list(self._by_trigger_event.keys())

    def get_replacements_for_event(self, event: str) -> List[ActiveEffect]:
        return list(self._by_replacement_event.get(event, []))

    def get_continuous_for_layer(self, layer: int) -> List[ActiveEffect]:
        return list(self._by_layer.get(layer, []))

    def expire_by_step(self, step, active_player_id: int) -> None:
        step_key = getattr(step, "name", None) or str(step)
        to_remove: List[ActiveEffect] = []
        for effect in self.effects:
            duration_type = _extract_duration_type(effect)
            if not duration_type:
                continue
            if duration_type == "until_end_of_combat" and step_key == "END_COMBAT":
                to_remove.append(effect)
            elif duration_type == "until_end_of_turn" and step_key == "CLEANUP":
                to_remove.append(effect)
            elif duration_type == "until_your_next_turn" and step_key == "CLEANUP":
                if effect.controller_id == active_player_id:
                    to_remove.append(effect)
            elif duration_type == "until_your_next_upkeep" and step_key == "UPKEEP":
                if effect.controller_id == active_player_id:
                    to_remove.append(effect)
        for effect in to_remove:
            self._remove_effect(effect)

    def prune_until_condition(self, event, game_state) -> None:
        from ..conditions import evaluate_condition
        from ..state import ResolveContext

        to_remove: List[ActiveEffect] = []
        for effect in self.effects:
            duration = _extract_duration(effect)
            duration_type = getattr(duration, "type", None) if duration else None
            if duration_type != "until_condition":
                continue
            condition = getattr(duration, "condition", None)
            if not condition:
                continue
            condition_data = _to_dict(condition)
            context = ResolveContext(
                source_id=effect.source_id,
                controller_id=effect.controller_id,
                targets=dict(getattr(event, "payload", {}) or {}),
            )
            if not evaluate_condition(game_state, condition_data, context):
                to_remove.append(effect)
        for effect in to_remove:
            self._remove_effect(effect)

    def _remove_from_indices(self, effect: ActiveEffect) -> None:
        trigger_event = self._extract_trigger_event(effect)
        if trigger_event in self._by_trigger_event:
            self._safe_remove(self._by_trigger_event[trigger_event], effect)

        replacement_event = self._extract_replacement_event(effect)
        if replacement_event in self._by_replacement_event:
            self._safe_remove(self._by_replacement_event[replacement_event], effect)

        layer = self._extract_continuous_layer(effect)
        if layer in self._by_layer:
            self._safe_remove(self._by_layer[layer], effect)

    @staticmethod
    def _safe_remove(items: List[ActiveEffect], effect: ActiveEffect) -> None:
        try:
            items.remove(effect)
        except ValueError:
            return

    @staticmethod
    def _extract_trigger_event(effect: ActiveEffect) -> Optional[str]:
        if effect.effect_data.initiation.value != "triggered":
            return None
        trigger = effect.effect_data.trigger
        return getattr(trigger, "event", None) if trigger else None

    @staticmethod
    def _extract_replacement_event(effect: ActiveEffect) -> Optional[str]:
        body = effect.effect_data.effect
        if getattr(body, "kind", None) == "replacement":
            replaces = getattr(body, "replaces", None) or {}
            return replaces.get("event") or replaces.get("event_type")
        if getattr(body, "kind", None) == "prevention":
            prevents = getattr(body, "prevents", None) or {}
            return prevents.get("event") or prevents.get("event_type")
        return None

    @staticmethod
    def _extract_continuous_layer(effect: ActiveEffect) -> Optional[int]:
        body = effect.effect_data.effect
        if getattr(body, "kind", None) != "continuous":
            return None
        return getattr(body, "layer", None)

    def _remove_effect(self, effect: ActiveEffect) -> None:
        if effect in self.effects:
            self.effects.remove(effect)
        self._remove_from_indices(effect)
        if effect.source_id in self._by_source:
            self._safe_remove(self._by_source[effect.source_id], effect)


def _extract_duration(effect: ActiveEffect) -> Optional[object]:
    body = effect.effect_data.effect
    if getattr(body, "kind", None) != "continuous":
        return None
    return getattr(body, "duration", None)


def _extract_duration_type(effect: ActiveEffect) -> Optional[str]:
    duration = _extract_duration(effect)
    return getattr(duration, "type", None) if duration else None


def _to_dict(value) -> Dict:
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True)
    if isinstance(value, dict):
        return dict(value)
    return {}
