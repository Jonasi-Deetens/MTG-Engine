from __future__ import annotations

from typing import Any, Tuple

from axis3.rules.core.permissions import RulesPermissions
from axis3.rules.sba.checker import run_sbas


class GameRulesEngine:
    """
    Facade for MTG Comprehensive Rules (Regels).

    Separation of concerns:
      - Axis2 EffectExecutor → *what happens* when an effect resolves
      - GameRulesEngine     → *whether* an action is legal and *when* SBAs run

    Card parsers do not replace this layer. They complement it.
    """

    def __init__(self, game_state: Any):
        self.gs = game_state
        self.permissions = RulesPermissions(game_state)

    def run_state_based_actions(self) -> None:
        """CR 704 — loop until no state-based actions apply."""
        run_sbas(self.gs)

    def validate_cast(self, source_id: str, controller: int) -> Tuple[bool, str]:
        """
        CR 601 — high-level cast legality (zone + timing + priority).
        Does not pay costs or choose targets.
        """
        if not self.permissions.has_priority(controller):
            return False, "CR 117: Need priority to cast"

        obj = self.gs.get_object(source_id)
        if obj is None:
            return False, "Object not found"

        ok, msg = self.permissions.can_cast_from_hand(obj)
        if not ok:
            return False, msg

        if self.gs.registries.permissions.has(source_id, "may_cast_as_instant"):
            return True, ""

        if self.permissions.is_instant(obj):
            ok, msg = self.permissions.can_cast_instant_speed()
            return ok, msg

        # Sorcery, creature, enchantment, etc. default to sorcery speed
        if self.permissions.is_sorcery(obj) or not self.permissions.is_instant(obj):
            ok, msg = self.permissions.can_cast_at_sorcery_speed(controller)
            if not ok:
                return False, msg

        return True, ""

    def validate_play_land(self, card_id: str, player_id: int) -> Tuple[bool, str]:
        """CR 305 — play a land from hand."""
        ok, msg = self.permissions.can_play_land(player_id)
        if not ok:
            return False, msg

        obj = self.gs.get_object(card_id)
        if obj is None:
            return False, "Card not found"
        if card_id not in self.gs.players[player_id].hand:
            return False, "CR 305.1: Land must be in your hand"
        if not self.permissions.is_land(obj):
            return False, "Not a land card"
        return True, ""

    def validate_activate_ability(
        self, source_id: str, controller: int, *, is_mana_ability: bool = False
    ) -> Tuple[bool, str]:
        """CR 602 — activate an ability."""
        if not self.permissions.has_priority(controller):
            return False, "CR 117: Need priority to activate"

        if is_mana_ability:
            return True, ""

        # Non-mana activated abilities use the stack (sorcery speed unless instant)
        ok, msg = self.permissions.can_cast_instant_speed()
        return ok, msg

    def record_land_played(self, player_id: int) -> None:
        self.gs.turn.lands_played_this_turn[player_id] = (
            self.gs.turn.lands_played_this_turn.get(player_id, 0) + 1
        )

    def reset_land_plays_for_turn(self, active_player: int) -> None:
        """Called at beginning of active player's turn (CR 500.4)."""
        self.gs.turn.lands_played_this_turn[active_player] = 0
