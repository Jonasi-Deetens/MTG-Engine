from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

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
                self.registered.append(
                    RegisteredAbility(
                        source_id=obj.id,
                        controller_id=obj.controller_id,
                        trigger=runtime.trigger,
                        graph=graph,
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
        for entry in self.registered:
            if entry.trigger != event.type:
                continue
            if "object_id" in event.payload and event.payload["object_id"] != entry.source_id:
                continue
            if "source_id" in event.payload and event.payload["source_id"] != entry.source_id:
                continue

            context = ResolveContext(
                source_id=entry.source_id,
                controller_id=entry.controller_id,
                triggering_source_id=event.payload.get("object_id"),
                targets=dict(event.payload),
            )
            self.game_state.stack.push(
                StackItem(
                    kind="ability_graph",
                    payload={
                        "graph": entry.graph,
                        "context": context.__dict__,
                        "source_object_id": entry.source_id,
                    },
                    controller_id=entry.controller_id,
                )
            )


