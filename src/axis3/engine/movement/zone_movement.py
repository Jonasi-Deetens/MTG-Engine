# axis3/engine/movement/zone_movement.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.engine.casting.context import CastContext
from axis3.engine.casting.replacement_engine import ReplacementEngine


@dataclass
class ZoneMovementEngine:
    """
    Handles all zone movement in the Axis3 engine.

    This subsystem:
      - Applies replacement effects before moving a card
      - Publishes zone change events
      - Updates RuntimeObject.zone
      - Updates player zone lists
      - Triggers enter/leave battlefield hooks
      - Triggers layer recalculation
      - Integrates with the event bus

    It is fully mechanic-agnostic. Flashback, Unearth, Disturb, Blitz,
    Buyback, Escape, and other mechanics register replacement effects
    in the ReplacementEffectRegistry. This engine simply interprets them.
    """

    replacements: ReplacementEngine

    # ============================================================
    # PUBLIC API
    # ============================================================

    def move_card(
        self,
        game_state: Any,
        obj_id: str,
        to_zone: str,
        controller: Optional[int] = None,
        ctx: Optional[CastContext] = None,
    ):
        """
        Move a card between zones with full replacement-effect support.

        ctx is optional:
          - Provided when movement is part of spell resolution
          - None when movement is caused by other effects
        """
        obj = game_state.get_object(obj_id)
        if obj is None:
            raise ValueError(f"Runtime object {obj_id} not found")

        from_zone = obj.zone
        to_zone = to_zone.upper()

        # 1. Build the initial zone change event
        event = Event(
            type=EventType.ZONE_CHANGE,
            payload={
                "obj_id": obj_id,
                "from_zone": from_zone,
                "to_zone": to_zone,
                "controller": controller if controller is not None else obj.controller,
                "ctx": ctx,
            },
        )

        # 2. Apply replacement effects (Flashback exile, Unearth exile, etc.)
        event = self.replacements.apply_zone_change_replacements(
            event, ctx, game_state
        )

        # Replacement effects may modify the destination zone
        final_to_zone = event.payload["to_zone"]

        # 3. Publish the (possibly modified) event
        game_state.event_bus.publish(event)

        # 4. Update the object's zone lists and zone field
        self._update_zones(game_state, obj, from_zone, final_to_zone)

        # 5. Update the object's controller if provided
        if controller is not None:
            obj.controller = controller

        # 6. Enter/leave battlefield hooks
        if self._is_battlefield(final_to_zone):
            self._apply_etb_replacements(game_state, obj)
            self._fire_etb_triggers(game_state, obj)

        if self._is_battlefield(from_zone):
            self._fire_ltb_triggers(game_state, obj)

        # 7. Reapply layers after zone movement
        game_state.layers.apply_all_layers()

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _update_zones(self, game_state: Any, obj: Any, from_zone: str, to_zone: str):
        """
        Remove the object from its old zone and add it to the new zone.
        """

        # Remove from old zone
        old_list = game_state.zone_list(obj.controller, str(from_zone).upper())
        if obj.id in old_list:
            old_list.remove(obj.id)

        # Add to new zone
        new_list = game_state.zone_list(obj.controller, str(to_zone).upper())
        new_list.append(obj.id)

        # Update the object's zone field
        obj.zone = to_zone

    def _is_battlefield(self, zone: Any) -> bool:
        """
        Helper to check if a zone (string or enum) is the battlefield.
        """
        if zone is None:
            return False
        return str(zone).upper().endswith("BATTLEFIELD")

    # ------------------------------------------------------------
    # ETB / LTB hooks
    # ------------------------------------------------------------

    def _apply_etb_replacements(self, game_state: Any, obj: Any):
        """
        Apply ETB replacement effects from the card definition, e.g.:
          - enters with counters
          - enters tapped
          - enters as a copy
        """
        card = getattr(obj, "axis3_card", None)
        if not card:
            return

        for repl in getattr(card, "replacement_effects", []):
            # Convention: event identifiers are simple strings like "enter_battlefield"
            if getattr(repl, "event", None) == "enter_battlefield":
                repl.apply(game_state, obj)

    def _fire_etb_triggers(self, game_state: Any, obj: Any):
        """
        Queue ETB triggered abilities, e.g.:
          - "When this enters the battlefield, draw a card"
        """
        card = getattr(obj, "axis3_card", None)
        if not card:
            return

        for trig in getattr(card, "triggered_abilities", []):
            if getattr(trig, "event", None) == "enter_battlefield":
                # Convention: TriggeredAbility provides a .queue(game_state, source_obj) API
                trig.queue(game_state, obj)

    def _fire_ltb_triggers(self, game_state: Any, obj: Any):
        """
        Queue leave-the-battlefield and dies triggers, e.g.:
          - "When this leaves the battlefield, ..."
          - "When this creature dies, ..."
        """
        card = getattr(obj, "axis3_card", None)
        if not card:
            return

        for trig in getattr(card, "triggered_abilities", []):
            event_name = getattr(trig, "event", None)
            if event_name in ("leave_battlefield", "dies"):
                trig.queue(game_state, obj)
