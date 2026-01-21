"""Stack resolution logic extracted from TurnManager."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..state import GameState, ResolveContext
    from ..stack import StackItem

logger = logging.getLogger(__name__)


@dataclass
class ResolveResult:
    """Result of resolving a stack item."""

    success: bool
    item_kind: str
    fizzled: bool = False
    reason: Optional[str] = None
    object_id: Optional[str] = None


class StackResolver:
    """Resolves stack items (spells and abilities).

    Responsible for:
    - Resolving spell stack items
    - Resolving ability_graph stack items
    - Handling fizzle conditions
    - Moving objects to appropriate zones after resolution
    """

    def __init__(self, game_state: "GameState") -> None:
        self._gs = game_state

    def resolve_top(self) -> Optional[ResolveResult]:
        """Pop and resolve the top item from the stack.

        Returns None if the stack is empty.
        """
        if self._gs.stack.is_empty():
            return None

        item = self._gs.stack.pop()
        return self.resolve_item(item)

    def resolve_item(self, item: "StackItem") -> ResolveResult:
        """Resolve a stack item."""
        self._gs.log(f"[graph] resolving stack item kind={item.kind} payload={item.payload}")
        print(f"[graph] resolving stack item kind={item.kind} payload={item.payload}", flush=True)

        if item.kind == "spell":
            return self._resolve_spell(item)
        elif item.kind == "ability_graph":
            return self._resolve_ability_graph(item)
        else:
            self._gs.log(f"Resolved stack item {item.kind}")
            return ResolveResult(success=True, item_kind=item.kind)

    def _resolve_spell(self, item: "StackItem") -> ResolveResult:
        """Resolve a spell stack item."""
        from ..events import Event
        from ..state import ResolveContext
        from ..targets import has_legal_targets, has_missing_required_targets, normalize_targets
        from ..zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND

        payload = item.payload or {}
        obj_id = payload.get("object_id")
        copy_of = payload.get("copy_of")
        is_copy = bool(payload.get("is_copy"))
        destination_zone = payload.get("destination_zone")

        obj = self._gs.objects.get(obj_id or copy_of) if (obj_id or copy_of) else None
        context_data = payload.get("context") or {}
        context = ResolveContext(**context_data)

        if obj:
            if context.source_id is None:
                context.source_id = obj.id
            normalize_targets(self._gs, context)
            missing_required = has_missing_required_targets(context)

            if not has_legal_targets(self._gs, context, allow_partial=True):
                # Spell fizzles
                if not is_copy:
                    self._gs.move_object(obj.id, ZONE_GRAVEYARD)
                    obj.was_cast = False
                    self._gs.event_bus.publish(Event(
                        type="spell_fizzled",
                        payload={
                            "object_id": obj.id,
                            "controller_id": obj.controller_id,
                            "reason": "missing_targets" if missing_required else "illegal_targets",
                        },
                    ))
                    reason = "missing_targets" if missing_required else "illegal_targets"
                    self._gs.log(f"Spell fizzles ({reason}): {obj_id}")
                else:
                    reason = "missing_targets" if missing_required else "illegal_targets"
                    self._gs.log(f"Spell copy fizzles ({reason}): {copy_of}")

                return ResolveResult(
                    success=False,
                    item_kind="spell",
                    fizzled=True,
                    reason=reason,
                    object_id=obj_id,
                )
            else:
                # Spell resolves successfully
                if not is_copy:
                    if destination_zone:
                        resolved_destination = destination_zone
                    elif "Instant" in obj.types or "Sorcery" in obj.types:
                        resolved_destination = ZONE_GRAVEYARD
                    else:
                        resolved_destination = ZONE_BATTLEFIELD

                    if context.choices.get("buyback_paid") and resolved_destination == ZONE_GRAVEYARD:
                        resolved_destination = ZONE_HAND

                    if resolved_destination == ZONE_BATTLEFIELD:
                        enter_copy_of = context.choices.get("enter_copy_of")
                        if enter_copy_of:
                            source = self._gs.objects.get(enter_copy_of)
                            if source:
                                self._gs.object_manager.apply_enter_copy(obj, source)
                        enter_choices = context.choices.get("enter_choices")
                        if isinstance(enter_choices, dict):
                            self._gs.object_manager.apply_enter_choices(obj, enter_choices)

                    self._gs.move_object(obj.id, resolved_destination)
                    obj.was_cast = False
                    self._gs.event_bus.publish(Event(
                        type="spell_resolved",
                        payload={"object_id": obj.id, "controller_id": obj.controller_id},
                    ))
                    self._gs.log(f"Resolved spell {obj_id}")
                else:
                    self._gs.event_bus.publish(Event(
                        type="spell_resolved",
                        payload={"copy_of": copy_of, "controller_id": context.controller_id},
                    ))
                    self._gs.log(f"Resolved spell copy of {copy_of}")

                return ResolveResult(success=True, item_kind="spell", object_id=obj_id)
        else:
            self._gs.log(f"Resolved spell {obj_id or copy_of}")
            return ResolveResult(success=True, item_kind="spell", object_id=obj_id)

    def _resolve_ability_graph(self, item: "StackItem") -> ResolveResult:
        """Resolve an ability_graph stack item."""
        from ..ability_graph import AbilityGraphRuntimeAdapter
        from ..choices import validate_enter_choices, validate_modal_choices
        from ..events import Event
        from ..state import ResolveContext
        from ..targets import normalize_targets, validate_targets
        from ..zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND

        payload = item.payload or {}
        is_copy = bool(payload.get("is_copy"))
        graph = payload.get("graph")
        context_data = payload.get("context") or {}
        context = ResolveContext(**context_data)

        try:
            node_count = len(graph.get("nodes", [])) if isinstance(graph, dict) else 0
            message = f"[graph] ability_graph resolve start nodes={node_count} copy={is_copy}"
            self._gs.log(message)
            print(message, flush=True)

            if context.source_id is None and payload.get("copy_of"):
                context.source_id = payload.get("copy_of")

            normalize_targets(self._gs, context)
            validate_targets(self._gs, context, allow_partial=True)

            adapter = AbilityGraphRuntimeAdapter(self._gs)
            if graph:
                validate_enter_choices(graph, context.__dict__)
                validate_modal_choices(graph, context.__dict__)
                adapter.resolve(graph, context)

            message = "[graph] ability_graph resolve done"
            self._gs.log(message)
            print(message, flush=True)

            # Handle destination zone for spell-like abilities
            source_id = payload.get("source_object_id")
            destination_zone = payload.get("destination_zone")
            if source_id and destination_zone and not is_copy:
                obj = self._gs.objects.get(source_id)
                if obj:
                    resolved_destination = destination_zone
                    if context.choices.get("buyback_paid") and resolved_destination == ZONE_GRAVEYARD:
                        resolved_destination = ZONE_HAND
                    if resolved_destination == ZONE_BATTLEFIELD:
                        if graph and not obj.ability_graphs:
                            obj.ability_graphs = [graph]
                            if not obj.base_ability_graphs:
                                obj.base_ability_graphs = [graph]
                        enter_copy_of = context.choices.get("enter_copy_of")
                        if enter_copy_of:
                            source = self._gs.objects.get(enter_copy_of)
                            if source:
                                self._gs.object_manager.apply_enter_copy(obj, source)
                        enter_choices = context.choices.get("enter_choices")
                        if isinstance(enter_choices, dict):
                            self._gs.object_manager.apply_enter_choices(obj, enter_choices)
                    self._gs.move_object(obj.id, resolved_destination)
                    obj.was_cast = False

            if context.source_id:
                self._gs.event_bus.publish(Event(
                    type="ability_resolved",
                    payload={"source_id": context.source_id, "controller_id": context.controller_id},
                ))

            self._gs.log("Resolved ability graph")
            return ResolveResult(success=True, item_kind="ability_graph")

        except ValueError as exc:
            message = f"[graph] ability_graph resolve error: {exc}"
            self._gs.log(message)
            print(message, flush=True)

            if "missing target" in str(exc).lower():
                self._gs.log("Ability fizzles (no targets chosen)")
                reason = "missing_targets"
            else:
                self._gs.log(f"Ability fizzles: {exc}")
                reason = "error"

            # Move spell object to destination zone on fizzle
            source_id = payload.get("source_object_id")
            destination_zone = payload.get("destination_zone")
            if source_id and destination_zone:
                obj = self._gs.objects.get(source_id)
                if obj:
                    self._gs.move_object(obj.id, destination_zone)
                    obj.was_cast = False
                    self._gs.event_bus.publish(Event(
                        type="spell_fizzled",
                        payload={
                            "object_id": obj.id,
                            "controller_id": obj.controller_id,
                            "reason": reason,
                        },
                    ))

            return ResolveResult(
                success=False,
                item_kind="ability_graph",
                fizzled=True,
                reason=reason,
            )

    def check_fizzle(self, item: "StackItem") -> bool:
        """Check if a stack item would fizzle (all targets illegal).

        Returns True if the item would fizzle.
        """
        from ..state import ResolveContext
        from ..targets import has_legal_targets, normalize_targets

        payload = item.payload or {}
        context_data = payload.get("context") or {}
        context = ResolveContext(**context_data)

        if item.kind == "spell":
            obj_id = payload.get("object_id")
            obj = self._gs.objects.get(obj_id) if obj_id else None
            if obj:
                if context.source_id is None:
                    context.source_id = obj.id
                normalize_targets(self._gs, context)
                return not has_legal_targets(self._gs, context, allow_partial=True)
        elif item.kind == "ability_graph":
            if context.source_id is None and payload.get("copy_of"):
                context.source_id = payload.get("copy_of")
            normalize_targets(self._gs, context)
            return not has_legal_targets(self._gs, context, allow_partial=True)

        return False
