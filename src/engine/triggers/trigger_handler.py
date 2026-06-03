"""Trigger handling for event matching and stack pushing."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..events import Event
    from ..state import GameState, ResolveContext
    from ..stack import StackItem

logger = logging.getLogger(__name__)


class TriggerHandler:
    """Handler for matching events to triggers and pushing to stack.

    Responsible for:
    - Matching events to registered triggers
    - Building ResolveContext for triggered abilities
    - Ordering triggers by APNAP (Active Player, Non-Active Player)
    - Pushing triggered abilities onto the stack
    """

    def __init__(self, game_state: "GameState") -> None:
        self._game_state = game_state

    @staticmethod
    def _normalize_trigger_card_types(card_type: Any) -> List[str]:
        if not card_type:
            return []
        if isinstance(card_type, (list, tuple, set)):
            values = [str(entry).strip().lower() for entry in card_type if entry]
            return [value for value in values if value]
        if isinstance(card_type, str):
            return [part.strip().lower() for part in card_type.split(",") if part.strip()]
        return [str(card_type).strip().lower()]

    def handle_event(self, event: "Event") -> List["StackItem"]:
        """Handle an event by matching triggers and adding to pending_triggers.

        Triggers are not pushed to the stack immediately. They are added to
        pending_triggers and will be pushed when priority is checked/synced.

        Returns the list of StackItems that were created (but not yet pushed).
        """
        from ..stack import StackItem
        from ..state import ResolveContext

        message = f"[graph] event {event.type} payload={event.payload}"
        self._game_state.log(message)
        print(message, flush=True)

        self._game_state.active_effect_registry.prune_until_condition(event, self._game_state)

        # Handle unified effect triggers (canonical effect graphs)
        return self._handle_unified_triggers(event)

    def _handle_unified_triggers(self, event: "Event") -> List["StackItem"]:
        from ..effects.effect_resolver import EffectGraphResolver
        from ..stack import StackItem
        from ..state import ResolveContext
        from ..conditions import evaluate_conditions

        created_items: List[StackItem] = []
        registry = self._game_state.active_effect_registry
        active_effects = registry.get_triggered_for_event(event.type)

        for active in active_effects:
            effect_data = active.effect_data
            trigger = effect_data.trigger
            if not trigger:
                continue

            if not self._matches_unified_trigger(active, event):
                continue

            context = self._build_unified_context(active, event)
            if effect_data.conditions:
                conditions = [_to_dict(c) for c in effect_data.conditions]
                if not evaluate_conditions(self._game_state, conditions, context):
                    continue

            graph = active.effect_graph
            if not graph:
                continue

            if effect_data.resolution.value == "immediate":
                resolver = EffectGraphResolver(self._game_state)
                resolver.resolve(graph, context, start_step_id=active.step_id)
                continue

            pending_entry = {
                "kind": "effect_graph",
                "payload": {
                    "graph": graph.model_dump(by_alias=True),
                    "start_step_id": active.step_id,
                    "context": context.__dict__,
                    "source_object_id": active.source_id,
                    "effect_id": active.effect_id,
                },
                "controller_id": active.controller_id,
            }
            self._game_state.pending_triggers.append(pending_entry)

            created_items.append(StackItem(
                kind="effect_graph",
                payload=pending_entry["payload"],
                controller_id=active.controller_id,
            ))

        return created_items

    def match_triggers(self, event: "Event") -> List[RegisteredTrigger]:
        """Find all triggers that match an event."""
        matching = []
        print(f"[graph] match_triggers event={event.type} registered_count={len(self._registry.registered)}", flush=True)
        for entry in self._registry.registered:
            print(f"[graph] checking trigger source={entry.source_id} trigger={entry.trigger} trigger_data={entry.trigger_data}", flush=True)
            if entry.trigger != event.type:
                continue

            # For card_enters and enters_battlefield, use specialized matching
            # that handles cardType filtering properly (e.g., "aura" subtype check)
            if entry.trigger in ("card_enters", "enters_battlefield"):
                if not self._matches_card_enters(entry, event):
                    continue
            else:
                if not self._matches_scope(entry, event):
                    continue
                if not self._matches_type(entry, event):
                    continue

            matching.append(entry)

        return matching

    def build_context(self, trigger: RegisteredTrigger, event: "Event") -> "ResolveContext":
        """Build a ResolveContext for a triggered ability."""
        from ..state import ResolveContext

        event_obj = None
        obj_id = event.payload.get("object_id")
        if obj_id:
            event_obj = self._game_state.objects.get(obj_id)

        # Determine triggering_aura_id
        triggering_aura_id = None
        card_types = event.payload.get("cardTypes") or []
        
        # Check if this is an Aura - look in cardTypes, object types, and type_line
        is_aura = "Aura" in card_types
        if not is_aura and event_obj:
            is_aura = "Aura" in (event_obj.types or [])
            # Also check type_line for "Aura" subtype
            if not is_aura and event_obj.type_line:
                is_aura = "aura" in event_obj.type_line.lower()
        
        if is_aura:
            triggering_aura_id = event.payload.get("object_id")

        context = ResolveContext(
            source_id=trigger.source_id,
            controller_id=trigger.controller_id,
            triggering_source_id=event.payload.get("object_id"),
            triggering_aura_id=triggering_aura_id,
            targets=dict(event.payload),
        )

        return context

    def _build_unified_context(self, active, event: "Event") -> "ResolveContext":
        from ..state import ResolveContext

        event_obj = None
        obj_id = event.payload.get("object_id")
        if obj_id:
            event_obj = self._game_state.objects.get(obj_id)

        triggering_aura_id = None
        card_types = event.payload.get("cardTypes") or []
        is_aura = "Aura" in card_types
        if not is_aura and event_obj:
            is_aura = "Aura" in (event_obj.types or [])
            if not is_aura and event_obj.type_line:
                is_aura = "aura" in event_obj.type_line.lower()

        if is_aura:
            triggering_aura_id = event.payload.get("object_id")

        return ResolveContext(
            source_id=active.source_id,
            controller_id=active.controller_id,
            triggering_source_id=event.payload.get("object_id"),
            triggering_aura_id=triggering_aura_id,
            targets=dict(event.payload),
        )

    def _matches_unified_trigger(self, active, event: "Event") -> bool:
        trigger = active.effect_data.trigger
        if not trigger:
            return False

        if trigger.event != event.type:
            return False

        if trigger.event in ("card_enters", "enters_battlefield"):
            return self._matches_unified_card_enters(active, event)

        if not self._matches_unified_scope(active, event):
            return False

        if not self._matches_unified_type(active, event):
            return False

        return True

    def _matches_unified_scope(self, active, event: "Event") -> bool:
        scope = getattr(active.effect_data.trigger, "scope", None) or "self"
        if scope == "any":
            return True
        if scope == "self":
            if "object_id" in event.payload and event.payload["object_id"] != active.source_id:
                return False
            if "source_id" in event.payload and event.payload["source_id"] != active.source_id:
                return False
            return True

        controller_id = self._resolve_event_controller_id(event)
        if controller_id is None:
            return False
        if scope in ("you", "you_control"):
            return controller_id == active.controller_id
        if scope in ("opponent", "opponent_control"):
            return controller_id != active.controller_id
        return False

    def _matches_unified_card_enters(self, active, event: "Event") -> bool:
        trigger = active.effect_data.trigger
        if not trigger:
            return False
        scope = getattr(trigger, "scope", None) or "self"

        if scope == "self" and event.payload.get("object_id") != active.source_id:
            return False

        if scope in ("you", "you_control", "opponent", "opponent_control"):
            controller_id = event.payload.get("controller_id")
            if controller_id is None:
                controller_id = self._resolve_event_controller_id(event)
            if controller_id is None:
                return False
            if scope in ("you", "you_control") and controller_id != active.controller_id:
                return False
            if scope in ("opponent", "opponent_control") and controller_id == active.controller_id:
                return False

        enters_where = getattr(trigger, "entersWhere", None)
        enters_from = getattr(trigger, "entersFrom", None)
        card_type = getattr(trigger, "cardType", None)

        payload_where = event.payload.get("entersWhere")
        payload_from = event.payload.get("entersFrom")
        payload_types = event.payload.get("cardTypes", [])

        if enters_where and payload_where and enters_where != payload_where:
            return False
        if enters_from and payload_from and enters_from != payload_from:
            return False

        card_types = self._normalize_trigger_card_types(card_type)
        if not card_types:
            return True

        normalized_types = {str(t).lower() for t in payload_types if isinstance(t, str)}
        obj_id = event.payload.get("object_id")
        obj = None
        if obj_id:
            obj = self._game_state.objects.get(obj_id)
            if obj:
                for t in (obj.types or []):
                    normalized_types.add(str(t).lower())
                if obj.type_line:
                    for part in obj.type_line.replace("—", "-").split("-"):
                        for word in part.strip().split():
                            normalized_types.add(word.lower())

        if "permanent" in card_types:
            return any(
                t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"}
                for t in normalized_types
            )
        if "noncreature" in card_types:
            if "creature" in normalized_types:
                return False
            remaining = [card_type for card_type in card_types if card_type != "noncreature"]
            if not remaining:
                return True
            return any(card_type in normalized_types for card_type in remaining)

        return any(card_type in normalized_types for card_type in card_types)

    def _matches_unified_type(self, active, event: "Event") -> bool:
        trigger = active.effect_data.trigger
        if not trigger:
            return False
        card_type = getattr(trigger, "cardType", None)
        card_types = self._normalize_trigger_card_types(card_type)
        if not card_types:
            return True

        obj = self._resolve_event_object(event)
        if not obj:
            return False

        normalized_types = {str(t).lower() for t in obj.types or []}
        if obj.type_line:
            for part in obj.type_line.replace("—", "-").split("-"):
                for word in part.strip().split():
                    normalized_types.add(word.lower())

        if "permanent" in card_types:
            return any(
                t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"}
                for t in normalized_types
            )
        if "noncreature" in card_types:
            if "creature" in normalized_types:
                return False
            remaining = [card_type for card_type in card_types if card_type != "noncreature"]
            if not remaining:
                return True
            return any(card_type in normalized_types for card_type in remaining)

        return any(card_type in normalized_types for card_type in card_types)

    def _order_triggers(
        self,
        entries: List[RegisteredTrigger],
        event: "Event",
    ) -> List[RegisteredTrigger]:
        """Order triggers by APNAP (Active Player, Non-Active Player)."""
        if len(entries) <= 1:
            return entries

        player_order = self._active_player_order()
        if not player_order:
            return entries

        ordered: List[RegisteredTrigger] = []
        for player_id in player_order:
            player_entries = [entry for entry in entries if entry.controller_id == player_id]
            if not player_entries:
                continue
            ordered.extend(self._order_player_triggers(player_entries, event, player_id))

        return ordered

    def _order_player_triggers(
        self,
        entries: List[RegisteredTrigger],
        event: "Event",
        player_id: int,
    ) -> List[RegisteredTrigger]:
        """Order a single player's triggers (may require player choice)."""
        if len(entries) <= 1:
            return entries

        choice_key = f"trigger_order:{player_id}:{event.type}"
        chosen = self._game_state.choices.get(choice_key)
        if isinstance(chosen, list) and chosen:
            key_map = {self._entry_key(entry): entry for entry in entries}
            ordered = [key_map[key] for key in chosen if key in key_map]
            remaining = [entry for entry in entries if entry not in ordered]
            return ordered + remaining

        # Queue a choice for the player
        pending = self._game_state.choices.get("pending")
        if not isinstance(pending, list):
            pending = []
        pending.append({
            "type": "trigger_order",
            "key": choice_key,
            "player_id": player_id,
            "options": [self._entry_key(entry) for entry in entries],
        })
        self._game_state.choices["pending"] = pending
        self._game_state.log(f"Trigger order choice missing for player {player_id}; default order applied.")
        return entries

    def _entry_key(self, entry: RegisteredTrigger) -> str:
        """Generate a unique key for a registered trigger."""
        return f"{entry.source_id}:{hash(str(entry.graph))}"

    def _active_player_order(self) -> List[int]:
        """Get player IDs in APNAP order."""
        if not self._game_state.players:
            return []

        start = getattr(self._game_state.turn, "active_player_index", 0) or 0
        order = []
        for offset in range(len(self._game_state.players)):
            idx = (start + offset) % len(self._game_state.players)
            player = self._game_state.players[idx]
            if getattr(player, "has_lost", False):
                continue
            order.append(player.id)
        return order

    def _matches_scope(self, entry: RegisteredTrigger, event: "Event") -> bool:
        """Check if a trigger matches the event's scope."""
        scope = (entry.trigger_data or {}).get("scope") or "self"

        if scope == "any":
            return True

        if scope == "self":
            if "object_id" in event.payload and event.payload["object_id"] != entry.source_id:
                return False
            if "source_id" in event.payload and event.payload["source_id"] != entry.source_id:
                return False
            return True

        controller_id = self._resolve_event_controller_id(event)
        if controller_id is None:
            return False

        if scope in ("you", "you_control"):
            return controller_id == entry.controller_id
        if scope in ("opponent", "opponent_control"):
            return controller_id != entry.controller_id

        return False

    def _resolve_event_controller_id(self, event: "Event") -> Optional[int]:
        """Resolve the controller ID from an event payload."""
        payload = event.payload

        # First check explicit controller_id in payload
        if "controller_id" in payload:
            return payload["controller_id"]

        # Then try to find from object references
        obj_id = payload.get("object_id")
        if obj_id:
            obj = self._game_state.objects.get(obj_id)
            if obj:
                return obj.controller_id

        source_id = payload.get("source_id")
        if source_id:
            obj = self._game_state.objects.get(source_id)
            if obj:
                return obj.controller_id

        target_id = payload.get("target_id")
        if target_id:
            obj = self._game_state.objects.get(target_id)
            if obj:
                return obj.controller_id

        attacker_id = payload.get("attacker_id")
        if attacker_id:
            obj = self._game_state.objects.get(attacker_id)
            if obj:
                return obj.controller_id

        # Check player ID fields
        for player_key in ("player_id", "target_player_id"):
            if payload.get(player_key) is not None:
                return int(payload[player_key])

        return None

    def _matches_card_enters(self, entry: RegisteredTrigger, event: "Event") -> bool:
        """Check if a trigger matches a card_enters event."""
        trigger_data = entry.trigger_data or {}
        scope = trigger_data.get("scope") or "self"

        if scope == "self" and event.payload.get("object_id") != entry.source_id:
            return False

        if scope in ("you", "you_control", "opponent", "opponent_control"):
            controller_id = event.payload.get("controller_id")
            if controller_id is None:
                controller_id = self._resolve_event_controller_id(event)
            if controller_id is None:
                return False
            if scope in ("you", "you_control") and controller_id != entry.controller_id:
                return False
            if scope in ("opponent", "opponent_control") and controller_id == entry.controller_id:
                return False

        enters_where = trigger_data.get("entersWhere")
        enters_from = trigger_data.get("entersFrom")
        card_type = trigger_data.get("cardType")

        payload_where = event.payload.get("entersWhere")
        payload_from = event.payload.get("entersFrom")
        payload_types = event.payload.get("cardTypes", [])

        if enters_where and payload_where and enters_where != payload_where:
            return False
        if enters_from and payload_from and enters_from != payload_from:
            return False

        card_types = self._normalize_trigger_card_types(card_type)
        if not card_types:
            return True

        normalized_types = {str(t).lower() for t in payload_types if isinstance(t, str)}
        
        # Also check the actual object for types/subtypes (Aura might be in type_line but not types)
        obj_id = event.payload.get("object_id")
        obj = None
        if obj_id:
            obj = self._game_state.objects.get(obj_id)
            if obj:
                # Add types from the object
                for t in (obj.types or []):
                    normalized_types.add(str(t).lower())
                # Parse type_line for subtypes (e.g., "Enchantment - Aura" -> add "aura")
                if obj.type_line:
                    for part in obj.type_line.replace("—", "-").split("-"):
                        for word in part.strip().split():
                            normalized_types.add(word.lower())
        
        card_types = [card_type.lower() for card_type in card_types]
        
        # Debug logging for trigger matching
        print(f"[graph] _matches_card_enters trigger_source={entry.source_id} event_obj={obj_id} "
              f"card_type={card_type} normalized_types={normalized_types} "
              f"type_line={getattr(obj, 'type_line', None) if obj else None}", flush=True)

        if "permanent" in card_types:
            return any(
                t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"}
                for t in normalized_types
            )
        if "noncreature" in card_types:
            if "creature" in normalized_types:
                return False
            remaining = [card_type for card_type in card_types if card_type != "noncreature"]
            if not remaining:
                return True
            return any(card_type in normalized_types for card_type in remaining)

        return any(card_type in normalized_types for card_type in card_types)

    def _matches_type(self, entry: RegisteredTrigger, event: "Event") -> bool:
        """Check if a trigger matches the event object's type."""
        trigger_data = entry.trigger_data or {}
        card_type = trigger_data.get("cardType")
        card_types = self._normalize_trigger_card_types(card_type)
        if not card_types:
            return True

        obj = self._resolve_event_object(event)
        if not obj:
            return False

        normalized_types = {str(t).lower() for t in obj.types or []}
        
        # Also check type_line for subtypes (e.g., "Enchantment — Aura" -> "aura")
        if obj.type_line:
            for part in obj.type_line.replace("—", "-").split("-"):
                for word in part.strip().split():
                    normalized_types.add(word.lower())
        
        if "permanent" in card_types:
            return any(
                t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"}
                for t in normalized_types
            )

        return any(card_type in normalized_types for card_type in card_types)

    def _resolve_event_object(self, event: "Event"):
        """Resolve the game object from an event payload."""
        payload = event.payload
        for key in ("object_id", "source_id", "target_id", "attacker_id"):
            obj_id = payload.get(key)
            if obj_id:
                obj = self._game_state.objects.get(obj_id)
                if obj:
                    return obj
        return None

    def _check_trigger_conditions(self, entry: RegisteredTrigger, context: "ResolveContext") -> bool:
        """Check if the trigger's conditions would pass given the context.
        
        This prevents triggers from being queued if their conditions will fail,
        avoiding unnecessary stack items that would just resolve and do nothing.
        
        Returns True if all conditions pass (or if there are no conditions).
        """
        from ..conditions import evaluate_condition
        
        graph = entry.graph
        if not graph or not isinstance(graph, dict):
            return True
        
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        root_id = graph.get("rootNodeId")
        
        if not nodes or not root_id:
            return True
        
        # Build edge map to find condition nodes that come right after the trigger
        edge_map: Dict[str, List[str]] = {}
        for edge in edges:
            from_id = edge.get("from_") or edge.get("from")
            to_id = edge.get("to")
            if from_id and to_id:
                if from_id not in edge_map:
                    edge_map[from_id] = []
                edge_map[from_id].append(to_id)
        
        # Find the root node (trigger node)
        root_node = None
        for node in nodes:
            if node.get("id") == root_id:
                root_node = node
                break
        
        if not root_node:
            return True
        
        # Check only CONDITION nodes that are direct children of the trigger
        # These are "gating" conditions that should prevent the trigger from firing
        children_ids = edge_map.get(root_id, [])
        
        for child_id in children_ids:
            for node in nodes:
                if node.get("id") == child_id and node.get("type") == "CONDITION":
                    condition_data = node.get("data", {})
                    if not condition_data:
                        continue
                    
                    # Evaluate the condition
                    result = evaluate_condition(self._game_state, condition_data, context)
                    
                    print(
                        f"[graph] trigger condition check node={child_id} "
                        f"type={condition_data.get('type')} result={result}",
                        flush=True
                    )
                    
                    if not result:
                        return False
        
        return True


def _to_dict(value: Any) -> Dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True)
    if isinstance(value, dict):
        return dict(value)
    return {}
