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
    - Resolving ability_graph stack items
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
        if item and item.kind == "ability_graph":
            payload = item.payload or {}
            graph = payload.get("graph") or {}
            ability_type = graph.get("abilityType")
            has_destination = "destination_zone" in payload
            
            print(f"[graph] resolve_top: ability_type={ability_type} has_destination={has_destination}", flush=True)
            
            # Determine if we should check for search choices:
            # - Spell graphs: always check
            # - Triggered abilities being CAST (has destination_zone): skip check (will be stored on object)
            # - Triggered abilities FIRING (no destination_zone): check (the ability is executing)
            is_casting_permanent_with_trigger = has_destination and ability_type == "triggered"
            should_check_search = not is_casting_permanent_with_trigger
            
            print(f"[graph] resolve_top: is_casting_permanent_with_trigger={is_casting_permanent_with_trigger} should_check_search={should_check_search}", flush=True)
            
            if should_check_search:
                # Check if search choices are needed
                pending_choices = self._check_search_choices_needed(item, provided_context)
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

    def _check_search_choices_needed(
        self, item: "StackItem", provided_context: Optional[Dict[str, Any]] = None
    ) -> List[PendingSearchChoice]:
        """Check if the stack item needs search choices that aren't provided.
        
        Returns list of pending choices needed, or empty list if all provided.
        """
        from ..effects_zone import _filter_search_pool, _matches_card_type_or_subtype
        from ..state import ResolveContext
        from ..zones import ZONE_LIBRARY
        
        print(f"[graph] _check_search_choices_needed called, provided_context={provided_context}", flush=True)
        
        payload = item.payload or {}
        graph = payload.get("graph")
        if not graph or not isinstance(graph, dict):
            print("[graph] _check_search_choices_needed: no graph", flush=True)
            return []
        
        nodes = graph.get("nodes", [])
        context_data = payload.get("context") or {}
        context = ResolveContext(**context_data)
        controller_id = context.controller_id
        if controller_id is None:
            print("[graph] _check_search_choices_needed: no controller_id", flush=True)
            return []
        
        # Get provided targets_by_effect
        provided_targets = {}
        if provided_context and "targets_by_effect" in provided_context:
            provided_targets = provided_context["targets_by_effect"]
        
        print(f"[graph] _check_search_choices: controller={controller_id} provided_targets={provided_targets}", flush=True)
        
        pending_choices: List[PendingSearchChoice] = []
        
        for node in nodes:
            if node.get("type") != "EFFECT":
                continue
            data = node.get("data", {})
            if data.get("type") != "search":
                continue
            
            node_id = node.get("id")
            zone = data.get("zone", ZONE_LIBRARY)
            
            print(f"[graph] found search node {node_id}", flush=True)
            
            # Check if selection was already provided for this node
            node_targets = provided_targets.get(node_id, {}) if node_id else {}
            search_results = node_targets.get("search_results_by_player", {})
            
            # Also check context targets_by_effect
            ctx_targets = context_data.get("targets_by_effect", {})
            ctx_node_targets = ctx_targets.get(node_id, {}) if node_id else {}
            ctx_search_results = ctx_node_targets.get("search_results_by_player", {})
            
            # Merge search results
            all_search_results = {**ctx_search_results, **search_results}
            
            print(f"[graph] search node {node_id}: all_search_results={all_search_results}", flush=True)
            
            # Check if player has provided a selection
            player_selection = all_search_results.get(str(controller_id)) or all_search_results.get(controller_id)
            
            print(f"[graph] search node {node_id}: player_selection={player_selection}", flush=True)
            
            if player_selection is not None:
                # Selection provided (even if empty list = declined)
                print(f"[graph] search node {node_id}: selection already provided, skipping", flush=True)
                continue
            
            # No selection provided - need to build options
            player = self._gs.get_player(controller_id)
            if not player:
                continue
            
            pool = getattr(player, zone, [])
            if not pool:
                continue
            
            # Filter the pool
            filtered_pool = _filter_search_pool(self, data, context, controller_id, pool)
            
            if not filtered_pool:
                # No valid options, no choice needed
                continue
            
            # Build options for frontend
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
                node_id=node_id,
                player_id=controller_id,
                zone=zone,
                options=options,
                min_selections=data.get("min", 0),
                max_selections=data.get("max", 1),
                source_id=context.source_id,
            ))
            print(f"[graph] search node {node_id}: added pending choice with {len(options)} options", flush=True)
        
        print(f"[graph] _check_search_choices_needed returning {len(pending_choices)} pending choices", flush=True)
        return pending_choices

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
            # Determine if we should run the graph:
            # - Spell graphs: always run
            # - Triggered abilities being CAST (has destination_zone): skip (will be stored on object)
            # - Triggered abilities FIRING (no destination_zone): run (the ability is executing)
            ability_type = graph.get("abilityType") if graph else None
            has_destination = "destination_zone" in payload
            is_casting_permanent_with_trigger = has_destination and ability_type == "triggered"
            should_run_graph = not is_casting_permanent_with_trigger
            if graph and should_run_graph:
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
                        # Always store graph on object for trigger registration
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
