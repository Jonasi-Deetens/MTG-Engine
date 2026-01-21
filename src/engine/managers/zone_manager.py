"""Zone management for game objects."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ..core.types import (
    ZONE_BATTLEFIELD,
    ZONE_COMMAND,
    ZONE_EXILE,
    ZONE_GRAVEYARD,
    ZONE_HAND,
    ZONE_LIBRARY,
)

if TYPE_CHECKING:
    from ..state import GameObject, PlayerState

logger = logging.getLogger(__name__)


@dataclass
class MoveResult:
    """Result of a zone move operation."""

    success: bool
    object_id: str
    from_zone: str
    to_zone: str
    was_token_removed: bool = False
    was_redirected: bool = False
    original_destination: Optional[str] = None


class ZoneManager:
    """Manages zone operations for game objects.

    Responsible for:
    - Moving objects between zones
    - Adding/removing objects from zone lists
    - Querying objects in zones
    - Shuffling libraries
    """

    def __init__(
        self,
        objects: Dict[str, "GameObject"],
        players: List["PlayerState"],
        get_player: Callable[[int], "PlayerState"],
    ) -> None:
        self._objects = objects
        self._players = players
        self._get_player = get_player

    def add_to_zone(self, zone: str, obj_id: str) -> None:
        """Add an object to a zone list."""
        obj = self._objects.get(obj_id)
        if not obj:
            return

        if zone == ZONE_BATTLEFIELD:
            player = self._get_player(obj.controller_id)
            if obj_id not in player.battlefield:
                player.battlefield.append(obj_id)
            return

        owner = self._get_player(obj.owner_id)

        if zone == ZONE_LIBRARY:
            if obj_id not in owner.library:
                owner.library.append(obj_id)
        elif zone == ZONE_HAND:
            if obj_id not in owner.hand:
                owner.hand.append(obj_id)
        elif zone == ZONE_GRAVEYARD:
            if obj_id not in owner.graveyard:
                owner.graveyard.append(obj_id)
        elif zone == ZONE_EXILE:
            if obj_id not in owner.exile:
                owner.exile.append(obj_id)
        elif zone == ZONE_COMMAND:
            if obj_id not in owner.command:
                owner.command.append(obj_id)
        elif zone.startswith("battlefield:"):
            controller_id = int(zone.split(":")[1])
            player = self._get_player(controller_id)
            if obj_id not in player.battlefield:
                player.battlefield.append(obj_id)

    def remove_from_zone(self, zone: str, obj_id: str) -> None:
        """Remove an object from a zone list."""
        obj = self._objects.get(obj_id)
        if not obj:
            return

        if zone == ZONE_BATTLEFIELD:
            for player in self._players:
                self._safe_remove(player.battlefield, obj_id)
            return

        owner = self._get_player(obj.owner_id)

        if zone == ZONE_LIBRARY:
            self._safe_remove(owner.library, obj_id)
        elif zone == ZONE_HAND:
            self._safe_remove(owner.hand, obj_id)
        elif zone == ZONE_GRAVEYARD:
            self._safe_remove(owner.graveyard, obj_id)
        elif zone == ZONE_EXILE:
            self._safe_remove(owner.exile, obj_id)
        elif zone == ZONE_COMMAND:
            self._safe_remove(owner.command, obj_id)
        elif zone.startswith("battlefield:"):
            controller_id = int(zone.split(":")[1])
            self._safe_remove(self._get_player(controller_id).battlefield, obj_id)

    def get_objects_in_zone(
        self,
        zone: str,
        controller_id: Optional[int] = None,
        owner_id: Optional[int] = None,
    ) -> List["GameObject"]:
        """Get all objects in a specific zone, optionally filtered by controller/owner."""
        result = []
        for obj in self._objects.values():
            if obj.zone != zone:
                continue
            if controller_id is not None and obj.controller_id != controller_id:
                continue
            if owner_id is not None and obj.owner_id != owner_id:
                continue
            result.append(obj)
        return result

    def get_battlefield_objects(
        self,
        controller_id: Optional[int] = None,
        card_type: Optional[str] = None,
    ) -> List["GameObject"]:
        """Get objects on the battlefield, optionally filtered."""
        result = []
        for obj in self._objects.values():
            if obj.zone != ZONE_BATTLEFIELD:
                continue
            if controller_id is not None and obj.controller_id != controller_id:
                continue
            if card_type is not None and card_type not in obj.types:
                continue
            result.append(obj)
        return result

    def shuffle_library(self, player_id: int) -> None:
        """Shuffle a player's library."""
        player = self._get_player(player_id)
        random.shuffle(player.library)

    def get_zone_list(self, zone: str, player_id: int) -> List[str]:
        """Get the list of object IDs in a zone for a player."""
        player = self._get_player(player_id)

        if zone == ZONE_LIBRARY:
            return player.library
        elif zone == ZONE_HAND:
            return player.hand
        elif zone == ZONE_GRAVEYARD:
            return player.graveyard
        elif zone == ZONE_EXILE:
            return player.exile
        elif zone == ZONE_COMMAND:
            return player.command
        elif zone == ZONE_BATTLEFIELD:
            return player.battlefield
        else:
            return []

    @staticmethod
    def _safe_remove(container: List[str], obj_id: str) -> None:
        """Safely remove an object ID from a list."""
        try:
            container.remove(obj_id)
        except ValueError:
            pass
