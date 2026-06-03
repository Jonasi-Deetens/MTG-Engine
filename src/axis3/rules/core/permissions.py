from __future__ import annotations

from typing import Any, List, Tuple

from axis3.state.zones import ZoneType


class RulesPermissions:
    """
    Comprehensive Rules checks that are independent of card parsing.

  These are the 'simple rules' — timing, priority, zone permissions — that
  every simulator must enforce even when card text is perfectly understood.
    """

    def __init__(self, game_state: Any):
        self.gs = game_state

    # ── Priority (CR 117) ─────────────────────────────────────

    def has_priority(self, player_id: int) -> bool:
        tm = getattr(self.gs, "turn_manager", None)
        if tm is None:
            return True
        return tm.priority.current == player_id

    def stack_is_empty(self) -> bool:
        return self.gs.stack.is_empty()

    # ── Turn structure (CR 500–514) ───────────────────────────

    def is_active_player(self, player_id: int) -> bool:
        return self.gs.turn.active_player == player_id

    def is_main_phase(self) -> bool:
        return self.gs.turn.is_main_phase()

    def is_precombat_main(self) -> bool:
        return self.gs.turn.is_precombat_main()

    def is_postcombat_main(self) -> bool:
        return self.gs.turn.is_postcombat_main()

  # ── Casting timing (CR 307, 601.3) ─────────────────────────

    def can_cast_at_sorcery_speed(self, controller: int) -> Tuple[bool, str]:
        if not self.is_main_phase():
            return False, "CR 307/601.3: Sorcery-speed spells only during main phase"
        if not self.stack_is_empty():
            return False, "CR 601.3a: Stack must be empty for sorcery-speed spells"
        return True, ""

    def can_cast_instant_speed(self) -> Tuple[bool, str]:
        # Instants and abilities with flash may be cast any time player has priority
        if not self.stack_is_empty():
            return True, ""
        return True, ""

    # ── Lands (CR 305) ──────────────────────────────────────

    def lands_played_this_turn(self, player_id: int) -> int:
        return self.gs.turn.lands_played_this_turn.get(player_id, 0)

    def max_lands_per_turn(self, player_id: int) -> int:
        bonus = 0
        if hasattr(self.gs, "layers"):
            bonus = self.gs.layers.get_land_play_bonus(player_id)
        return 1 + bonus

    def can_play_land(self, player_id: int) -> Tuple[bool, str]:
        if not self.has_priority(player_id):
            return False, "CR 117: Need priority to play a land"
        if not self.is_main_phase():
            return False, "CR 305.1: Lands only during main phase"
        if not self.stack_is_empty():
            return False, "CR 305.1: Stack must be empty to play a land"
        if self.lands_played_this_turn(player_id) >= self.max_lands_per_turn(player_id):
            return False, "CR 305.1: Already played maximum lands this turn"
        return True, ""

    # ── Object helpers ────────────────────────────────────────

    @staticmethod
    def get_card_types(obj: Any) -> List[str]:
        if getattr(obj, "axis2_card", None) and obj.axis2_card:
            return list(obj.axis2_card.characteristics.types or [])
        if getattr(obj, "axis3_card", None) and obj.axis3_card:
            return list(obj.axis3_card.types or [])
        if hasattr(obj, "has_type"):
            return []
        return []

    def is_instant(self, obj: Any) -> bool:
        return "Instant" in self.get_card_types(obj)

    def is_sorcery(self, obj: Any) -> bool:
        return "Sorcery" in self.get_card_types(obj)

    def is_land(self, obj: Any) -> bool:
        return "Land" in self.get_card_types(obj)

    def object_zone_name(self, obj: Any) -> str:
        z = obj.zone
        return z.name if hasattr(z, "name") else str(z).upper()

    def can_cast_from_hand(self, obj: Any) -> Tuple[bool, str]:
        zone = self.object_zone_name(obj)
        if zone == "HAND":
            return True, ""
        if self.gs.registries.permissions.has(obj.id, "may_cast_from_graveyard") and zone == "GRAVEYARD":
            return True, ""
        if self.gs.registries.permissions.has(obj.id, "may_cast_from_exile") and zone == "EXILE":
            return True, ""
        return False, f"CR 601.2a: Cannot cast from {zone}"
