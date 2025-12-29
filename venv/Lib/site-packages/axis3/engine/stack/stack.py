# src/axis3/engine/stack/stack.py

from typing import Any, Optional
from axis3.state.zones import ZoneType
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType


class Stack:
    def __init__(self):
        # stack items: either string ids or StackItem objects that contain an obj_id
        self.items: list[Any] = []

    def push(self, item: "StackItem"):
        self.items.append(item)

    def pop(self) -> Any:
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self) -> Optional[Any]:
        if not self.items:
            return None
        return self.items[-1]

    # alias that returns the top item id or None
    def top(self) -> Optional[Any]:
        return self.peek()

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def resolve_top(self, gs=None) -> Optional[str]:
        """
        Resolve the top stack item.

        If gs is provided, it will be used to access game state (recommended).
        Returns the resolved object id, or None if nothing resolved.
        """
        gs.add_debug_log(f"resolve_top: resolving top of stack")
        if self.is_empty():
            return None

        item = self.pop()

        # Support both plain ids and StackItem objects with an obj_id attribute
        obj_id = getattr(item, "obj_id", None) or getattr(item, "id", None) or item
        runtime_obj = gs.objects.get(obj_id) if gs is not None else None
        if runtime_obj is None:
            if gs is not None:
                gs.add_debug_log(f"resolve_top: runtime object {obj_id} not found")
            return None

        # Publish a SPELL_RESOLVE event so replacement effects can respond
        try:
            gs.event_bus.publish(Event(type=EventType.SPELL_RESOLVE, payload={"obj_id": obj_id}))
        except Exception:
            # If your event types or bus differ, adapt this call.
            pass

        # If the runtime object provides a custom resolution hook, use it
        if hasattr(runtime_obj, "resolve_on_stack"):
            try:
                runtime_obj.resolve_on_stack(gs)
            except Exception as e:
                gs.add_debug_log(f"resolve_top: error in resolve_on_stack for {obj_id}: {e}")
            return obj_id

        # Fallback resolution based on runtime object characteristics
        # Treat creature/land/artifact/enchantment/planeswalker spells as permanents
        is_permanent_spell = (
            runtime_obj.is_creature()
            or runtime_obj.is_land()
            or runtime_obj.has_type("Artifact")
            or runtime_obj.has_type("Enchantment")
            or runtime_obj.has_type("Planeswalker")
        )

        # inside resolve_top, after runtime_obj lookup
        gs.add_debug_log(f"resolve_top: resolving {obj_id} zone={runtime_obj.zone} controller={runtime_obj.controller} name={runtime_obj.name}")
        is_permanent_spell = (
            runtime_obj.is_creature()
            or runtime_obj.is_land()
            or runtime_obj.has_type("Artifact")
            or runtime_obj.has_type("Enchantment")
            or runtime_obj.has_type("Planeswalker")
        )
        gs.add_debug_log(f"resolve_top: is_permanent_spell={is_permanent_spell}")

        if is_permanent_spell:
            gs.add_debug_log(f"resolve_top: moving {obj_id} to battlefield")
            gs.move_card(obj_id, ZoneType.BATTLEFIELD, controller=runtime_obj.controller)
            gs.add_debug_log(f"resolve_top: moved {obj_id}, new zone={gs.objects[obj_id].zone}")
            return obj_id   # <-- CRITICAL
        else:
            gs.add_debug_log(f"resolve_top: resolving non-permanent {obj_id}, sending to graveyard")
            gs.move_card(obj_id, ZoneType.GRAVEYARD, controller=runtime_obj.controller)
            gs.add_debug_log(f"resolve_top: moved {obj_id}, new zone={gs.objects[obj_id].zone}")


        # Non-permanent spells: try to call a card-level resolve hook, then send to graveyard
        card_def = getattr(runtime_obj, "card_def", None)
        if card_def is not None and hasattr(card_def, "resolve_effect"):
            try:
                card_def.resolve_effect(gs, runtime_obj)
            except Exception as e:
                gs.add_debug_log(f"resolve_top: error resolving effect for {obj_id}: {e}")

        # Default: move non-permanent spells to graveyard
        try:
            gs.move_card(obj_id, ZoneType.GRAVEYARD, controller=runtime_obj.controller)
        except Exception as e:
            gs.add_debug_log(f"resolve_top: error moving {obj_id} to graveyard: {e}")

        return obj_id
