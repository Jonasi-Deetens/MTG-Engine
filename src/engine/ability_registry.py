from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .ability_graph import AbilityGraphRuntimeAdapter
from .events import Event
from .state import GameObject, GameState, ResolveContext
from .stack import StackItem


@dataclass
class RegisteredAbility:
    source_id: str
    controller_id: int
    trigger: str
    graph: Dict
    trigger_data: Optional[Dict]


class AbilityRegistry:
    def __init__(self, game_state: GameState) -> None:
        self.game_state = game_state
        self.adapter = AbilityGraphRuntimeAdapter(game_state)
        self.registered: List[RegisteredAbility] = []
        self._register_from_objects()
        self._subscribe()

    def _register_from_objects(self) -> None:
        for obj in self.game_state.objects.values():
            self._register_object(obj)

    def _register_object(self, obj: GameObject) -> None:
        for graph in obj.ability_graphs:
            runtime = self.adapter.build_runtime(graph)
            if runtime.trigger:
                if any(
                    entry.source_id == obj.id
                    and entry.trigger == runtime.trigger
                    and entry.graph is graph
                    for entry in self.registered
                ):
                    continue
                self.registered.append(
                    RegisteredAbility(
                        source_id=obj.id,
                        controller_id=obj.controller_id,
                        trigger=runtime.trigger,
                        graph=graph,
                        trigger_data=runtime.trigger_data,
                    )
                )

    def _unregister_object(self, obj_id: str) -> None:
        self.registered = [entry for entry in self.registered if entry.source_id != obj_id]

    def _subscribe(self) -> None:
        triggers = {entry.trigger for entry in self.registered}
        special_triggers = {"enters_battlefield", "leaves_battlefield"}
        for trigger in triggers - special_triggers:
            self.game_state.event_bus.subscribe(trigger, self._handle_event)
        if "enters_battlefield" in triggers:
            self.game_state.event_bus.subscribe("enters_battlefield", self._handle_enters)
        if "leaves_battlefield" in triggers:
            self.game_state.event_bus.subscribe("leaves_battlefield", self._handle_leaves)

    def _handle_enters(self, event: Event) -> None:
        obj_id = event.payload.get("object_id")
        if not obj_id:
            return
        obj = self.game_state.objects.get(obj_id)
        if obj:
            self._register_object(obj)
        self._handle_event(event)

    def _handle_leaves(self, event: Event) -> None:
        self._handle_event(event)
        obj_id = event.payload.get("object_id")
        if obj_id:
            self._unregister_object(obj_id)

    def _handle_event(self, event: Event) -> None:
        matching = []
        for entry in self.registered:
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
        for entry in self._order_triggers(matching, event):
            context = ResolveContext(
                source_id=entry.source_id,
                controller_id=entry.controller_id,
                triggering_source_id=event.payload.get("object_id"),
                targets=dict(event.payload),
            )
            self.game_state.stack.push(StackItem(
                kind="ability_graph",
                payload={
                    "graph": entry.graph,
                    "context": context.__dict__,
                    "source_object_id": entry.source_id,
                },
                controller_id=entry.controller_id,
            ))

    def _order_triggers(self, entries: List[RegisteredAbility], event: Event) -> List[RegisteredAbility]:
        if len(entries) <= 1:
            return entries
        player_order = self._active_player_order()
        if not player_order:
            return entries
        ordered: List[RegisteredAbility] = []
        for player_id in player_order:
            player_entries = [entry for entry in entries if entry.controller_id == player_id]
            if not player_entries:
                continue
            ordered.extend(self._order_player_triggers(player_entries, event, player_id))
        return ordered

    def _order_player_triggers(
        self,
        entries: List[RegisteredAbility],
        event: Event,
        player_id: int,
    ) -> List[RegisteredAbility]:
        if len(entries) <= 1:
            return entries
        choice_key = f"trigger_order:{player_id}:{event.type}"
        chosen = self.game_state.choices.get(choice_key)
        if isinstance(chosen, list) and chosen:
            key_map = {self._entry_key(entry): entry for entry in entries}
            ordered = [key_map[key] for key in chosen if key in key_map]
            remaining = [entry for entry in entries if entry not in ordered]
            return ordered + remaining
        pending = self.game_state.choices.get("pending")
        if not isinstance(pending, list):
            pending = []
        pending.append({
            "type": "trigger_order",
            "key": choice_key,
            "player_id": player_id,
            "options": [self._entry_key(entry) for entry in entries],
        })
        self.game_state.choices["pending"] = pending
        self.game_state.log(f"Trigger order choice missing for player {player_id}; default order applied.")
        return entries

    def _entry_key(self, entry: RegisteredAbility) -> str:
        return f"{entry.source_id}:{hash(str(entry.graph))}"

    def _active_player_order(self) -> List[int]:
        if not self.game_state.players:
            return []
        start = getattr(self.game_state.turn, "active_player_index", 0) or 0
        order = []
        for offset in range(len(self.game_state.players)):
            idx = (start + offset) % len(self.game_state.players)
            player = self.game_state.players[idx]
            if getattr(player, "has_lost", False):
                continue
            order.append(player.id)
        return order

    def _matches_scope(self, entry: RegisteredAbility, event: Event) -> bool:
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

    def _resolve_event_controller_id(self, event: Event) -> Optional[int]:
        payload = event.payload
        obj_id = payload.get("object_id")
        if obj_id:
            obj = self.game_state.objects.get(obj_id)
            if obj:
                return obj.controller_id
        source_id = payload.get("source_id")
        if source_id:
            obj = self.game_state.objects.get(source_id)
            if obj:
                return obj.controller_id
        target_id = payload.get("target_id")
        if target_id:
            obj = self.game_state.objects.get(target_id)
            if obj:
                return obj.controller_id
        attacker_id = payload.get("attacker_id")
        if attacker_id:
            obj = self.game_state.objects.get(attacker_id)
            if obj:
                return obj.controller_id
        for player_key in ("player_id", "target_player_id"):
            if payload.get(player_key) is not None:
                return int(payload[player_key])
        return None

    def _matches_card_enters(self, entry: RegisteredAbility, event: Event) -> bool:
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
            return any(t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"} for t in normalized_types)
        return card_type in normalized_types

    def _matches_type(self, entry: RegisteredAbility, event: Event) -> bool:
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
            return any(t in {"creature", "artifact", "enchantment", "planeswalker", "land", "battle"} for t in normalized_types)
        return card_type in normalized_types

    def _resolve_event_object(self, event: Event):
        payload = event.payload
        for key in ("object_id", "source_id", "target_id", "attacker_id"):
            obj_id = payload.get(key)
            if obj_id:
                obj = self.game_state.objects.get(obj_id)
                if obj:
                    return obj
        return None


