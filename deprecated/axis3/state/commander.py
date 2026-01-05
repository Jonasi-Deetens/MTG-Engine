# axis3/state/commander.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class CommanderEngine:
    """
    Provides commander-related utilities for the Axis3 engine.

    This subsystem is intentionally small and mechanic-agnostic.
    It supports:
      - Flashback reductions based on commander mana value
      - Eminence abilities
      - Commander tax
      - "If your commander is on the battlefield or in the command zone..."
      - Any future commander-based mechanics

    GameState owns an instance of this engine.
    """

    game_state: Any

    # ============================================================
    # COMMANDER LOOKUP
    # ============================================================

    def get_commanders(self, controller_id: int) -> List[Any]:
        """
        Return all commander RuntimeObjects owned by the player.
        """

        player = self.game_state.players[controller_id]
        commanders = []

        # Command zone
        for obj_id in player.command:
            obj = self.game_state.get_object(obj_id)
            if obj is not None:
                commanders.append(obj)

        # Battlefield (partner commanders, etc.)
        for obj_id in player.battlefield:
            obj = self.game_state.get_object(obj_id)
            if obj is not None and getattr(obj, "is_commander", False):
                commanders.append(obj)

        return commanders

    # ============================================================
    # COMMANDER MANA VALUE
    # ============================================================

    def greatest_commander_mana_value(self, controller_id: int) -> int:
        """
        Return the highest mana value among the player's commanders
        (in command zone or on battlefield).
        """

        commanders = self.get_commanders(controller_id)
        if not commanders:
            return 0

        return max(getattr(cmd, "mana_value", 0) for cmd in commanders)

    # ============================================================
    # COMMANDER TAX
    # ============================================================

    def commander_tax_for(self, commander_obj: Any) -> int:
        """
        Compute commander tax for a specific commander object.
        """

        casts = getattr(commander_obj, "commander_cast_count", 0)
        return casts * 2  # Commander tax is +2 per previous cast

    def apply_commander_tax(self, commander_obj: Any, base_cost: str) -> str:
        """
        Add commander tax to a mana cost string.
        """

        tax = self.commander_tax_for(commander_obj)
        if tax == 0:
            return base_cost

        # Insert tax as generic mana
        return f"{{{tax}}}" + base_cost

    # ============================================================
    # COMMANDER PRESENCE CHECKS
    # ============================================================

    def commander_is_present(self, controller_id: int) -> bool:
        """
        True if the player has a commander on the battlefield or in the command zone.
        """

        return len(self.get_commanders(controller_id)) > 0

    def commander_on_battlefield(self, controller_id: int) -> bool:
        """
        True if the player controls a commander on the battlefield.
        """

        player = self.game_state.players[controller_id]

        for obj_id in player.battlefield:
            obj = self.game_state.get_object(obj_id)
            if obj is not None and getattr(obj, "is_commander", False):
                return True

        return False

    def commander_in_command_zone(self, controller_id: int) -> bool:
        """
        True if the player's commander is in the command zone.
        """

        player = self.game_state.players[controller_id]
        return len(player.command) > 0
