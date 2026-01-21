"""Trigger handling for event matching and stack pushing."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .trigger_registry import RegisteredTrigger

if TYPE_CHECKING:
    from ..events import Event
    from ..state import GameState, ResolveContext
    from ..stack import StackItem
    from .trigger_registry import TriggerRegistry

logger = logging.getLogger(__name__)


class TriggerHandler:
    """Handler for matching events to triggers and pushing to stack.

    Responsible for:
    - Matching events to registered triggers
    - Building ResolveContext for triggered abilities
    - Ordering triggers by APNAP (Active Player, Non-Active Player)
    - Pushing triggered abilities onto the stack
    """

    def __init__(
        self,
        registry: "TriggerRegistry",
        game_state: "GameState",
    ) -> None:
        self._registry = registry
        self._game_state = game_state

    def handle_event(self, event: "Event") -> List["StackItem"]:
        """Handle an event by matching triggers and pushing to stack.

        Returns the list of StackItems that were pushed.
        """
        from ..stack import StackItem
        from ..state import ResolveContext

        message = f"[graph] event {event.type} payload={event.payload}"
        self._game_state.log(message)
        print(message, flush=True)

        # Find matching triggers
        matching = self.match_triggers(event)

        # Order by APNAP
        ordered = self._order_triggers(matching, event)

        pushed_items: List[StackItem] = []
        for entry in ordered:
            message = (
                f"[graph] trigger match source={entry.source_id} "
                f"controller={entry.controller_id} trigger={entry.trigger}"
            )
            self._game_state.log(message)
            print(message, flush=True)

            # Build context
            context = self.build_context(entry, event)

            # Create and push stack item
            item = StackItem(
                kind="ability_graph",
                payload={
                    "graph": entry.graph,
                    "context": context.__dict__,
                    "source_object_id": entry.source_id,
                },
                controller_id=entry.controller_id,
            )
            self._game_state.stack.push(item)
            pushed_items.append(item)

            message = f"[graph] pushed ability_graph source={entry.source_id} trigger={entry.trigger}"
            self._game_state.log(message)
            print(message, flush=True)

        return pushed_items

    def match_triggers(self, event: "Event") -> List[RegisteredTrigger]:
        """Find all triggers that match an event."""
        matching = []
        for entry in self._registry.registered:
            if entry.trigger != event.type:
                continue

            if entry.trigger == "card_enters":
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
        if "Aura" in card_types:
            triggering_aura_id = event.payload.get("object_id")
        elif event_obj and "Aura" in (event_obj.types or []):
            triggering_aura_id = event_obj.id

        context = ResolveContext(
            source_id=trigger.source_id,
            controller_id=trigger.controller_id,
            triggering_source_id=event.payload.get("object_id"),
            triggering_aura_id=triggering_aura_id,
            targets=dict(event.payload),
        )

        return context

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

        if not card_type:
            return True

        normalized_types = {str(t).lower() for t in payload_types if isinstance(t, str)}
        card_type = str(card_type).lower()

        if card_type == "permanent":
            return any(
                t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"}
                for t in normalized_types
            )

        return card_type in normalized_types

    def _matches_type(self, entry: RegisteredTrigger, event: "Event") -> bool:
        """Check if a trigger matches the event object's type."""
        trigger_data = entry.trigger_data or {}
        card_type = trigger_data.get("cardType")

        if not card_type:
            return True

        obj = self._resolve_event_object(event)
        if not obj:
            return False

        normalized_types = {str(t).lower() for t in obj.types or []}
        card_type = str(card_type).lower()

        if card_type == "permanent":
            return any(
                t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"}
                for t in normalized_types
            )

        return card_type in normalized_types

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
