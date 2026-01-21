"""Replacement effect management."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ..state import GameObject

logger = logging.getLogger(__name__)


@dataclass
class ReplacementResult:
    """Result of applying a replacement effect."""

    applied: bool
    original_value: str
    replaced_value: str
    effect_id: Optional[str] = None
    needs_choice: bool = False
    choice_options: Optional[List[Dict[str, Any]]] = None


class ReplacementManager:
    """Manages replacement effects.

    Responsible for:
    - Registering replacement effects (global and per-object)
    - Applying zone change replacements
    - Applying object event replacements (destroy, sacrifice)
    - Handling multiple replacement choices
    """

    def __init__(
        self,
        replacement_effects: List[Dict[str, Any]],
        replacement_choices: Dict[str, str],
        queue_choice_fn: Callable[[Dict[str, Any]], None],
        log_fn: Callable[[str], None],
    ) -> None:
        self._replacement_effects = replacement_effects
        self._replacement_choices = replacement_choices
        self._queue_choice = queue_choice_fn
        self._log = log_fn
        self._counter = 0

    def next_effect_id(self) -> str:
        """Generate a unique replacement effect ID."""
        self._counter += 1
        return f"repl_{self._counter}"

    def register(self, effect: Dict[str, Any]) -> None:
        """Register a global replacement effect."""
        if "effect_id" not in effect:
            effect["effect_id"] = self.next_effect_id()
        self._replacement_effects.append(effect)

    def unregister(self, effect_id: str) -> bool:
        """Unregister a replacement effect by ID."""
        for i, effect in enumerate(self._replacement_effects):
            if effect.get("effect_id") == effect_id:
                self._replacement_effects.pop(i)
                return True
        return False

    def apply_zone_replacement(
        self,
        obj: "GameObject",
        from_zone: str,
        to_zone: str,
    ) -> str:
        """Apply replacement effects to a zone change.

        Returns the final destination zone after all replacements.
        """
        matches_all = self._gather_zone_matches(obj, from_zone, to_zone)

        if not matches_all:
            return to_zone

        event_key = f"{obj.id}:{from_zone}:{to_zone}"
        return self._apply_replacement(matches_all, event_key, obj.controller_id, to_zone)

    def apply_object_replacement(
        self,
        obj: "GameObject",
        effect_type: str,
        default_zone: str,
    ) -> str:
        """Apply replacement effects to an object event (destroy, sacrifice).

        Returns the final destination zone after all replacements.
        """
        matches_all = self._gather_object_matches(obj, effect_type)

        if not matches_all:
            return default_zone

        event_key = f"{obj.id}:{effect_type}"
        return self._apply_replacement(matches_all, event_key, obj.controller_id, default_zone)

    def _gather_zone_matches(
        self,
        obj: "GameObject",
        from_zone: str,
        to_zone: str,
    ) -> List[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
        """Gather all matching replacement effects for a zone change."""

        def matches(effect: Dict[str, Any]) -> bool:
            if effect.get("type") != "replace_zone_change":
                return False
            if effect.get("from_zone") and effect.get("from_zone") != from_zone:
                return False
            if effect.get("to_zone") and effect.get("to_zone") != to_zone:
                return False
            if effect.get("object_id") and effect.get("object_id") != obj.id:
                return False
            if effect.get("controller_id") is not None and effect.get("controller_id") != obj.controller_id:
                return False
            if effect.get("owner_id") is not None and effect.get("owner_id") != obj.owner_id:
                return False
            return True

        # Check object's temporary effects
        matches_temp = [effect for effect in list(obj.temporary_effects) if matches(effect)]
        # Check global replacement effects
        matches_global = [effect for effect in list(self._replacement_effects) if matches(effect)]

        return [(effect, obj.temporary_effects) for effect in matches_temp] + [
            (effect, self._replacement_effects) for effect in matches_global
        ]

    def _gather_object_matches(
        self,
        obj: "GameObject",
        effect_type: str,
    ) -> List[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
        """Gather all matching replacement effects for an object event."""

        def matches(effect: Dict[str, Any]) -> bool:
            if effect.get("type") != effect_type:
                return False
            if effect.get("object_id") and effect.get("object_id") != obj.id:
                return False
            if effect.get("controller_id") is not None and effect.get("controller_id") != obj.controller_id:
                return False
            if effect.get("owner_id") is not None and effect.get("owner_id") != obj.owner_id:
                return False
            return True

        # Check object's temporary effects
        matches_temp = [effect for effect in list(obj.temporary_effects) if matches(effect)]
        # Check global replacement effects
        matches_global = [effect for effect in list(self._replacement_effects) if matches(effect)]

        return [(effect, obj.temporary_effects) for effect in matches_temp] + [
            (effect, self._replacement_effects) for effect in matches_global
        ]

    def _apply_replacement(
        self,
        matches_all: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]],
        event_key: str,
        controller_id: int,
        default_value: str,
    ) -> str:
        """Apply a replacement effect from a list of matches."""
        if len(matches_all) > 1:
            # Multiple replacements - check for a choice or use most recent
            choice_id = self._replacement_choices.get(event_key)
            if choice_id:
                for effect, container in matches_all:
                    if effect.get("effect_id") == choice_id:
                        replacement = effect.get("replacement_zone")
                        if replacement:
                            self._consume(effect, container)
                            self._replacement_choices.pop(event_key, None)
                            return replacement

            # Queue a choice for the player
            self._queue_choice({
                "type": "zone_replacement" if ":" in event_key and len(event_key.split(":")) == 3 else "object_replacement",
                "key": event_key,
                "player_id": controller_id,
                "options": [
                    {"id": effect.get("effect_id"), "replacement_zone": effect.get("replacement_zone")}
                    for effect, _ in matches_all
                ],
            })

            # Default to most recent (highest timestamp)
            matches_all.sort(key=lambda item: int(item[0].get("timestamp_order", 0)), reverse=True)
            effect, container = matches_all[0]
            replacement = effect.get("replacement_zone")
            if replacement:
                self._consume(effect, container)
                self._log(f"Multiple replacements; defaulted to most recent.")
                return replacement

        # Single replacement or no choice needed
        for effect, container in matches_all:
            replacement = effect.get("replacement_zone")
            if replacement:
                self._consume(effect, container)
                return replacement

        return default_value

    def _consume(self, effect: Dict[str, Any], container: List[Dict[str, Any]]) -> None:
        """Consume a replacement effect (decrement uses or remove if exhausted)."""
        remaining = effect.get("uses")
        if remaining is None:
            return

        remaining = int(remaining) - 1
        if remaining <= 0:
            if effect in container:
                container.remove(effect)
        else:
            effect["uses"] = remaining
