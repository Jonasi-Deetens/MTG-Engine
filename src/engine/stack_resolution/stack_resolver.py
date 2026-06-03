"""Stack resolution logic extracted from TurnManager."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..state import GameState, ResolveContext
    from ..stack import StackItem

logger = logging.getLogger(__name__)


@dataclass
class PendingSearchChoice:
    """Represents a search choice that needs player input."""
    node_id: str
    player_id: int
    zone: str
    options: List[Dict[str, Any]]
    min_selections: int = 0
    max_selections: int = 1
    source_id: Optional[str] = None
    order_required: bool = False
    label: Optional[str] = None


@dataclass
class ResolveResult:
    """Result of resolving a stack item."""

    success: bool
    item_kind: str
    fizzled: bool = False
    reason: Optional[str] = None
    object_id: Optional[str] = None
    needs_input: bool = False
    pending_search_choices: List[PendingSearchChoice] = field(default_factory=list)


class StackResolver:
    """Resolves stack items (spells and abilities).

    Responsible for:
    - Resolving spell stack items
    - Resolving effect_graph stack items
    - Handling fizzle conditions
    - Moving objects to appropriate zones after resolution
    """

    def __init__(self, game_state: "GameState") -> None:
        self._gs = game_state

    def resolve_top(self, provided_context: Optional[Dict[str, Any]] = None) -> Optional[ResolveResult]:
        """Pop and resolve the top item from the stack.

        Args:
            provided_context: Optional context with choices like search_results to merge
                             into the stack item's context before resolution.

        Returns None if the stack is empty.
        """
        print(f"[graph] resolve_top called, stack_size={len(self._gs.stack.items)}, provided_context={provided_context}", flush=True)
        
        if self._gs.stack.is_empty():
            print("[graph] resolve_top: stack is empty", flush=True)
            return None

        # Peek first to check for needed choices
        item = self._gs.stack.peek()
        if item and item.kind == "effect_graph":
            payload = item.payload or {}
            graph = payload.get("graph") or {}
            has_destination = "destination_zone" in payload
            
            print(f"[graph] resolve_top: has_destination={has_destination}", flush=True)
            
            pending_choices = self._check_search_choices_needed_effect_graph(item, provided_context)
            if pending_choices:
                print(f"[graph] resolve_top: returning needs_input with {len(pending_choices)} choices", flush=True)
                # Don't pop - return result indicating input needed
                return ResolveResult(
                    success=False,
                    item_kind=item.kind,
                    needs_input=True,
                    pending_search_choices=pending_choices,
                )
            # Merge provided context before resolving
            if provided_context:
                print(f"[graph] resolve_top: merging provided_context", flush=True)
                self._merge_context_into_item(item, provided_context)

        print(f"[graph] resolve_top: popping stack item, stack_size_before={len(self._gs.stack.items)}", flush=True)
        item = self._gs.stack.pop()
        print(f"[graph] resolve_top: popped, stack_size_after={len(self._gs.stack.items)}", flush=True)
        return self.resolve_item(item)

    def _merge_context_into_item(self, item: "StackItem", provided_context: Dict[str, Any]) -> None:
        """Merge provided context (like search selections) into the stack item's context."""
        if not item.payload:
            item.payload = {}
        if "context" not in item.payload:
            item.payload["context"] = {}
        
        ctx = item.payload["context"]
        
        # Merge targets_by_effect
        if "targets_by_effect" in provided_context:
            if "targets_by_effect" not in ctx:
                ctx["targets_by_effect"] = {}
            for node_id, targets in provided_context["targets_by_effect"].items():
                if node_id not in ctx["targets_by_effect"]:
                    ctx["targets_by_effect"][node_id] = {}
                ctx["targets_by_effect"][node_id].update(targets)
        
        # Merge search_results directly into targets
        if "search_results" in provided_context:
            if "targets" not in ctx:
                ctx["targets"] = {}
            ctx["targets"]["search_results"] = provided_context["search_results"]
        
        # Merge search_results_by_player
        if "search_results_by_player" in provided_context:
            if "targets" not in ctx:
                ctx["targets"] = {}
            ctx["targets"]["search_results_by_player"] = provided_context["search_results_by_player"]

    def _check_search_choices_needed_effect_graph(
        self, item: "StackItem", provided_context: Optional[Dict[str, Any]] = None
    ) -> List[PendingSearchChoice]:
        from ..effects_zone import _filter_search_pool, _matches_card_type_or_subtype
        from ..state import ResolveContext
        from ..zones import ZONE_LIBRARY

        print(f"[graph] _check_search_choices_needed_effect_graph called, provided_context={provided_context}", flush=True)

        payload = item.payload or {}
        graph = payload.get("graph")
        if not graph or not isinstance(graph, dict):
            print("[graph] _check_search_choices_needed_effect_graph: no graph", flush=True)
            return []

        steps = graph.get("steps", [])
        context_data = payload.get("context") or {}
        context = ResolveContext(**context_data)
        controller_id = context.controller_id
        if controller_id is None:
            print("[graph] _check_search_choices_needed_effect_graph: no controller_id", flush=True)
            return []

        provided_targets = {}
        if provided_context and "targets_by_effect" in provided_context:
            provided_targets = provided_context["targets_by_effect"]

        pending_choices: List[PendingSearchChoice] = []

        def _has_selection(node_key: str) -> bool:
            if not node_key:
                return False
            node_targets = provided_targets.get(node_key, {}) if node_key else {}
            search_results = node_targets.get("search_results_by_player", {})
            ctx_targets = context_data.get("targets_by_effect", {})
            ctx_node_targets = ctx_targets.get(node_key, {}) if node_key else {}
            ctx_search_results = ctx_node_targets.get("search_results_by_player", {})
            all_search_results = {**ctx_search_results, **search_results}
            player_selection = all_search_results.get(str(controller_id)) or all_search_results.get(controller_id)
            return player_selection is not None

        for step in steps:
            if not isinstance(step, dict):
                continue
            step_id = step.get("id")
            effect = step.get("effect") or {}
            body = effect.get("effect") or {}
            if body.get("kind") != "one_shot":
                continue
            action = body.get("action") or {}
            action_type = action.get("type")
            if action_type not in ("search", "look_at_pick_and_bottom"):
                continue

            if action_type == "look_at_pick_and_bottom":
                pick_max = int(action.get("pickMax", 1))
                amount = int(action.get("amount", 1))
                if amount <= 0:
                    continue
                player = self._gs.get_player(controller_id)
                if not player:
                    continue
                top_ids = list(player.library[:amount])
                if not top_ids:
                    continue
                pick_types = action.get("pickTypes") or []
                if isinstance(pick_types, str):
                    pick_types = [pick_types]

                def matches_types(obj_id: str) -> bool:
                    if not pick_types:
                        return True
                    obj = self._gs.objects.get(obj_id)
                    if not obj:
                        return False
                    return any(_matches_card_type_or_subtype(obj, t) for t in pick_types if t)

                pick_candidates = [obj_id for obj_id in top_ids if matches_types(obj_id)]
                if pick_max > 0 and pick_candidates:
                    pick_node_id = f"{step_id}:pick" if step_id else None
                    if pick_node_id and not _has_selection(pick_node_id):
                        options = []
                        for obj_id in pick_candidates:
                            obj = self._gs.objects.get(obj_id)
                            if obj:
                                options.append({
                                    "id": obj_id,
                                    "name": obj.name,
                                    "mana_value": obj.mana_value,
                                    "type_line": obj.type_line,
                                })
                        pending_choices.append(PendingSearchChoice(
                            node_id=pick_node_id,
                            player_id=controller_id,
                            zone=f"top {amount}",
                            options=options,
                            min_selections=0,
                            max_selections=pick_max,
                            source_id=context.source_id,
                            label="Choose a card to reveal and put into hand",
                        ))

                if action.get("orderBottom", True) and top_ids:
                    order_node_id = f"{step_id}:order" if step_id else None
                    if order_node_id and not _has_selection(order_node_id):
                        options = []
                        for obj_id in top_ids:
                            obj = self._gs.objects.get(obj_id)
                            if obj:
                                options.append({
                                    "id": obj_id,
                                    "name": obj.name,
                                    "mana_value": obj.mana_value,
                                    "type_line": obj.type_line,
                                })
                        pending_choices.append(PendingSearchChoice(
                            node_id=order_node_id,
                            player_id=controller_id,
                            zone=f"top {amount}",
                            options=options,
                            min_selections=len(top_ids),
                            max_selections=len(top_ids),
                            source_id=context.source_id,
                            order_required=True,
                            label="Order the cards for the bottom",
                        ))
                continue

            zone = action.get("zone", ZONE_LIBRARY)

            node_targets = provided_targets.get(step_id, {}) if step_id else {}
            search_results = node_targets.get("search_results_by_player", {})

            ctx_targets = context_data.get("targets_by_effect", {})
            ctx_node_targets = ctx_targets.get(step_id, {}) if step_id else {}
            ctx_search_results = ctx_node_targets.get("search_results_by_player", {})

            all_search_results = {**ctx_search_results, **search_results}
            player_selection = all_search_results.get(str(controller_id)) or all_search_results.get(controller_id)
            if player_selection is not None:
                continue

            player = self._gs.get_player(controller_id)
            if not player:
                continue

            pool = getattr(player, zone, [])
            if not pool:
                continue

            filtered_pool = _filter_search_pool(self, action, context, controller_id, pool)
            if not filtered_pool:
                continue

            options = []
            for obj_id in filtered_pool:
                obj = self._gs.objects.get(obj_id)
                if obj:
                    options.append({
                        "id": obj_id,
                        "name": obj.name,
                        "mana_value": obj.mana_value,
                        "type_line": obj.type_line,
                    })

            pending_choices.append(PendingSearchChoice(
                node_id=step_id,
                player_id=controller_id,
                zone=zone,
                options=options,
                min_selections=action.get("min", 0),
                max_selections=action.get("max", 1),
                source_id=context.source_id,
            ))

        print(f"[graph] _check_search_choices_needed_effect_graph returning {len(pending_choices)} pending choices", flush=True)
        return pending_choices

    def resolve_item(self, item: "StackItem") -> ResolveResult:
        """Resolve a stack item."""
        self._gs.log(f"[graph] resolving stack item kind={item.kind} payload={item.payload}")
        print(f"[graph] resolving stack item kind={item.kind} payload={item.payload}", flush=True)

        if item.kind == "spell":
            return self._resolve_spell(item)
        elif item.kind == "effect_graph":
            return self._resolve_effect_graph(item)
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

    def _resolve_effect_graph(self, item: "StackItem") -> ResolveResult:
        """Resolve a unified effect_graph stack item."""
        from ..effects.effect_resolver import EffectGraphResolver
        from ..events import Event
        from ..state import ResolveContext
        from ..choices import validate_enter_choices_effect_graph, validate_modal_choices_effect_graph
        from ..targets import has_legal_targets, has_missing_required_targets, normalize_targets, validate_targets
        from ..zones import ZONE_BATTLEFIELD, ZONE_GRAVEYARD, ZONE_HAND

        payload = item.payload or {}
        graph = payload.get("graph")
        start_step_id = payload.get("start_step_id")
        context_data = payload.get("context") or {}
        context = ResolveContext(**context_data)
        is_copy = bool(payload.get("is_copy"))

        if context.source_id is None:
            context.source_id = payload.get("source_object_id") or payload.get("copy_of")
        if context.controller_id is None:
            context.controller_id = item.controller_id

        normalize_targets(self._gs, context)
        missing_required = has_missing_required_targets(context)
        if not has_legal_targets(self._gs, context, allow_partial=True):
            reason = "missing_targets" if missing_required else "illegal_targets"
            self._gs.log(f"Effect graph fizzles ({reason}): {context.source_id}")
            return ResolveResult(
                success=False,
                item_kind="effect_graph",
                fizzled=True,
                reason=reason,
                object_id=context.source_id,
            )

        validate_targets(self._gs, context, allow_partial=True)

        validate_enter_choices_effect_graph(graph, context.__dict__)
        validate_modal_choices_effect_graph(graph, context.__dict__)

        resolver = EffectGraphResolver(self._gs)
        resolver.resolve(graph, context, start_step_id=start_step_id)

        source_id = payload.get("source_object_id")
        destination_zone = payload.get("destination_zone")
        if source_id and destination_zone and not is_copy:
            obj = self._gs.objects.get(source_id)
            if obj:
                resolved_destination = destination_zone
                if context.choices.get("buyback_paid") and resolved_destination == ZONE_GRAVEYARD:
                    resolved_destination = ZONE_HAND
                if resolved_destination == ZONE_BATTLEFIELD:
                    if graph and not obj.effect_graphs:
                        obj.effect_graphs = [graph]
                        if not obj.base_effect_graphs:
                            obj.base_effect_graphs = [graph]
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
            resolved_event = "spell_resolved" if destination_zone else "ability_resolved"
            payload = (
                {"object_id": context.source_id, "controller_id": context.controller_id}
                if resolved_event == "spell_resolved"
                else {"source_id": context.source_id, "controller_id": context.controller_id}
            )
            self._gs.event_bus.publish(Event(type=resolved_event, payload=payload))

        return ResolveResult(success=True, item_kind="effect_graph")

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
        elif item.kind == "effect_graph":
            if context.source_id is None and payload.get("copy_of"):
                context.source_id = payload.get("copy_of")
            normalize_targets(self._gs, context)
            return not has_legal_targets(self._gs, context, allow_partial=True)

        return False
