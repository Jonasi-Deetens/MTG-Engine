# axis3/engine/casting/replacement_engine.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from axis3.engine.casting.context import CastContext
from axis3.state.registries import ReplacementEffectRegistry


@dataclass
class ReplacementEngine:
    """
    Applies replacement effects to events.

    This engine is fully mechanic-agnostic:
      - Flashback: exile on resolution
      - Unearth: exile if it would leave the battlefield
      - Disturb: exile on resolution
      - Blitz: sacrifice at end step, exile if it would die
      - Buyback: return to hand instead of graveyard
      - Escape: exile instead of going anywhere else
      - "If this creature would die, exile it instead"
      - "If this spell would be countered, exile it instead"

    Effects register themselves in ReplacementEffectRegistry.
    This engine simply interprets them.
    """

    replacements: ReplacementEffectRegistry

    # ============================================================
    # PUBLIC API
    # ============================================================

    def apply_to_event(self, event: Any, ctx: Optional[CastContext], game_state: Any) -> Any:
        """
        Apply all replacement effects that modify this event.

        event: a ZoneChangeEvent, SpellCounterEvent, etc.
        ctx: the CastContext for spell-related events (may be None)
        """

        source_id = event.payload.get("obj_id")
        if source_id is None:
            return event  # Not a card-related event

        # Get all replacement effects registered for this object
        effects = self.replacements.get(source_id)
        if not effects:
            return event

        # Apply effects in order of registration
        for effect in effects:
            if effect.applies_if(ctx):
                # The effect_fn returns a modified event or performs the action directly
                new_event = effect.effect_fn(game_state, event)
                if new_event is not None:
                    event = new_event

        return event

    # ============================================================
    # SPECIALIZED HELPERS
    # ============================================================

    def apply_zone_change_replacements(self, event: Any, ctx: Optional[CastContext], game_state: Any) -> Any:
        """
        Apply replacement effects specifically for zone changes.
        """

        if event.type != "ZONE_CHANGE":
            return event

        return self.apply_to_event(event, ctx, game_state)

    def apply_resolution_replacements(self, event: Any, ctx: CastContext, game_state: Any) -> Any:
        """
        Apply replacement effects that modify spell resolution.
        """

        if event.type != "SPELL_RESOLVE":
            return event

        return self.apply_to_event(event, ctx, game_state)
