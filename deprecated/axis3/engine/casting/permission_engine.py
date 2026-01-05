# axis3/engine/casting/permission_engine.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from axis3.state.registries import PermissionRegistry
from axis3.engine.casting.context import CastContext


@dataclass
class PermissionEngine:
    """
    Handles all permission checks for casting spells.

    This engine is intentionally mechanic-agnostic.
    Mechanics like Flashback, Escape, Madness, Disturb, Blitz, etc.
    simply register permissions in the PermissionRegistry.

    The PermissionEngine only interprets those permissions.
    """

    permissions: PermissionRegistry

    # ============================================================
    # Public API
    # ============================================================

    def can_cast_from_zone(self, ctx: CastContext, game_state: Any) -> bool:
        """
        Determine whether the spell can be cast from its current zone.
        """

        obj = game_state.get_object(ctx.source_id)
        if obj is None:
            ctx.set_illegal("Object not found")
            return False

        zone = obj.zone

        # 1. Normal casting rules
        if zone == "Hand":
            return True

        # 2. Permission-based casting rules
        if self.permissions.has(ctx.source_id, "may_cast_from_graveyard") and zone == "Graveyard":
            return True

        if self.permissions.has(ctx.source_id, "may_cast_from_exile") and zone == "Exile":
            return True

        if self.permissions.has(ctx.source_id, "may_cast_from_library") and zone == "Library":
            return True

        # 3. Command zone (e.g., Commander)
        if zone == "Command":
            if self.permissions.has(ctx.source_id, "may_cast_from_command_zone"):
                return True

        # 4. Otherwise illegal
        ctx.set_illegal(f"Cannot cast from zone: {zone}")
        return False

    def can_cast_now(self, ctx: CastContext, game_state: Any) -> bool:
        """
        Check timing restrictions (instant-speed vs sorcery-speed).
        """

        obj = game_state.get_object(ctx.source_id)
        if obj is None:
            ctx.set_illegal("Object not found")
            return False

        # If the spell has flash or permission to cast as instant
        if self.permissions.has(ctx.source_id, "may_cast_as_instant"):
            return True

        # If the spell is an instant, always OK
        if "Instant" in obj.types:
            return True

        # Otherwise must obey sorcery timing
        if not game_state.turn.is_main_phase():
            ctx.set_illegal("Not in main phase")
            return False

        if game_state.stack.has_items():
            ctx.set_illegal("Stack is not empty")
            return False

        return True

    def can_cast(self, ctx: CastContext, game_state: Any) -> bool:
        """
        Full permission check: zone + timing + global restrictions.
        """

        # 1. Zone-based permission
        if not self.can_cast_from_zone(ctx, game_state):
            return False

        # 2. Timing rules
        if not self.can_cast_now(ctx, game_state):
            return False

        # 3. Global restrictions
        for restriction in game_state.registries.global_restrictions.all():
            if not restriction.allows_cast(ctx, game_state):
                ctx.set_illegal("Global restriction prevents casting")
                return False

        return True
