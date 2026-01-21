"""Phase and step handling logic extracted from TurnManager."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from ..state import GameState, PlayerState
    from ..turn import Step

logger = logging.getLogger(__name__)


class PhaseHandler:
    """Handles phase/step-specific logic.

    Responsible for:
    - Untap step handling
    - Draw step handling
    - Combat damage step handling
    - Cleanup step handling
    - Temporary effect expiration
    - Discard to hand size
    - Activation limit resets
    """

    def __init__(
        self,
        game_state: "GameState",
        get_active_player_id: Callable[[], int],
    ) -> None:
        self._gs = game_state
        self._get_active_player_id = get_active_player_id

    def handle_untap(self) -> None:
        """Handle the untap step."""
        from ..events import Event
        from ..zones import ZONE_BATTLEFIELD

        active_player_id = self._get_active_player_id()
        self._gs.event_bus.publish(Event(
            type="untap",
            payload={"active_player": active_player_id}
        ))

        for obj_id in self._gs.get_player(active_player_id).battlefield:
            obj = self._gs.objects.get(obj_id)
            if obj:
                if obj.phased_out:
                    obj.phased_out = False
                    continue
                obj.tapped = False

    def handle_draw(self) -> None:
        """Handle the draw step."""
        active_player_id = self._get_active_player_id()
        turn = self._gs.turn

        # First player on first turn doesn't draw
        if turn.turn_number == 1 and turn.active_player_index == 0:
            return

        self.draw_cards(active_player_id, 1)

    def handle_combat_damage(self) -> None:
        """Handle the combat damage step."""
        from ..events import Event

        self._gs.event_bus.publish(Event(
            type="combat_damage",
            payload={"active_player": self._get_active_player_id()}
        ))

    def handle_cleanup(self) -> None:
        """Handle the cleanup step."""
        from ..zones import ZONE_BATTLEFIELD

        if os.getenv("ENGINE_TRACE") == "1":
            turn = self._gs.turn
            print(
                f"[engine] cleanup_step t{turn.turn_number} {turn.phase.value}:{turn.step.value}",
                flush=True,
            )

        # Clear damage and combat state from creatures
        for obj in self._gs.objects.values():
            if obj.zone == ZONE_BATTLEFIELD:
                obj.damage = 0
                obj.is_attacking = False
                obj.is_blocking = False

        # Discard to hand size
        active_player = self._gs.get_player(self._get_active_player_id())
        self.discard_to_hand_size(active_player)

        # Clear combat state
        self._gs.turn.combat_state = None

    def discard_to_hand_size(self, player: "PlayerState") -> None:
        """Discard down to maximum hand size."""
        from ..replacements import resolve_replacement
        from ..zones import ZONE_GRAVEYARD, ZONE_HAND

        max_hand_size = getattr(player, "max_hand_size", 7)
        if max_hand_size is None or max_hand_size < 0:
            return

        attempts = 0
        no_progress = 0

        while len(player.hand) > max_hand_size and player.hand:
            hand_len_before = len(player.hand)
            card_id = player.hand[-1]

            if os.getenv("ENGINE_TRACE") == "1":
                print(
                    f"[engine] discard_check player={player.id} hand={len(player.hand)} card={card_id}",
                    flush=True,
                )

            if card_id not in self._gs.objects:
                player.hand.pop()
                self._gs.log(f"Removed missing card id from hand: {card_id}")
                continue

            replacement = resolve_replacement(
                self._gs,
                "replace_discard",
                player.id,
                f"discard:event:cleanup:{player.id}",
            )
            attempts += 1

            if replacement:
                replacement_zone = replacement.get("replacement_zone")
                if replacement_zone == "skip":
                    if attempts >= len(player.hand):
                        break
                    player.hand.insert(0, player.hand.pop())
                    continue
                if replacement_zone == ZONE_HAND:
                    if attempts >= len(player.hand):
                        break
                    player.hand.insert(0, player.hand.pop())
                    continue
                if replacement_zone:
                    self._gs.move_object(card_id, replacement_zone)
                else:
                    self._gs.move_object(card_id, ZONE_GRAVEYARD)
            else:
                self._gs.move_object(card_id, ZONE_GRAVEYARD)

            if len(player.hand) >= hand_len_before:
                no_progress += 1
                if no_progress >= len(player.hand):
                    self._gs.log(f"Discard cleanup made no progress for player {player.id}; stopping.")
                    break
            else:
                no_progress = 0

    def expire_temporary_effects(self, step: "Step") -> None:
        """Expire temporary effects at the appropriate step."""
        from ..turn import Step

        active_player_id = self._get_active_player_id()

        for obj in self._gs.objects.values():
            if not obj.temporary_effects:
                continue

            remaining = []
            for effect in obj.temporary_effects:
                duration = effect.get("duration")
                controller_id = effect.get("controller_id")

                # Check if this effect should expire
                should_expire = False

                if duration == "until_end_of_combat" and step == Step.END_COMBAT:
                    should_expire = True
                elif duration == "until_end_of_turn" and step == Step.CLEANUP:
                    should_expire = True
                elif duration == "until_end_of_your_next_turn" and step == Step.CLEANUP:
                    if controller_id == active_player_id:
                        should_expire = True
                elif duration == "until_your_next_upkeep" and step == Step.UPKEEP:
                    if controller_id == active_player_id:
                        should_expire = True
                elif duration is None and "prevent_damage" in effect and step == Step.CLEANUP:
                    should_expire = True

                if should_expire:
                    # Handle cleanup for specific effect types
                    if effect.get("type") == "set_controller" and effect.get("original_controller") is not None:
                        obj.controller_id = effect.get("original_controller")
                    if effect.get("type") == "add_protection" and effect.get("protection"):
                        obj.protections.discard(effect.get("protection"))
                else:
                    remaining.append(effect)

            obj.temporary_effects = remaining

    def draw_cards(self, player_id: int, count: int) -> None:
        """Draw cards for a player."""
        from ..zones import ZONE_HAND

        player = self._gs.get_player(player_id)

        for _ in range(count):
            if not player.library:
                player.has_lost = True
                self._gs.log(f"Player {player.id} loses for drawing from empty library.")
                if not player.removed_from_game:
                    self._gs.remove_player_from_game(player.id)
                return

            card_id = player.library[0]
            if card_id not in self._gs.objects:
                player.library.pop(0)
                self._gs.log(f"Removed missing card id from library: {card_id}")
                continue

            self._gs.move_object(card_id, ZONE_HAND)

    def reset_activation_limits(self, scope: str) -> None:
        """Reset activation limits for a scope (turn, phase, combat)."""
        for obj in self._gs.objects.values():
            if not obj.activation_limits:
                continue
            to_remove = [key for key in obj.activation_limits if key.endswith(f":{scope}")]
            for key in to_remove:
                obj.activation_limits.pop(key, None)
