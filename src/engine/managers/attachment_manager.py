"""Attachment management for Auras and Equipment."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from ..core.types import ZONE_BATTLEFIELD, ZONE_GRAVEYARD

if TYPE_CHECKING:
    from ..state import GameObject

logger = logging.getLogger(__name__)


@dataclass
class AttachResult:
    """Result of an attachment operation."""

    success: bool
    object_id: str
    target_id: Optional[str] = None
    detached: bool = False
    reason: Optional[str] = None


class AttachmentManager:
    """Manages attachment relationships between objects.

    Responsible for:
    - Attaching Auras and Equipment to targets
    - Detaching when targets become illegal
    - Checking attachment legality
    - Enforcing attachment rules (SBA)
    """

    def __init__(
        self,
        objects: Dict[str, "GameObject"],
        move_object: Callable[[str, str], None],
    ) -> None:
        self._objects = objects
        self._move_object = move_object

    def attach(self, source_id: str, target_id: str) -> AttachResult:
        """Attach an object to a target."""
        source = self._objects.get(source_id)
        target = self._objects.get(target_id)

        if not source:
            return AttachResult(success=False, object_id=source_id, reason="Source not found")

        if not target:
            return AttachResult(success=False, object_id=source_id, reason="Target not found")

        if target.zone != ZONE_BATTLEFIELD:
            return AttachResult(
                success=False,
                object_id=source_id,
                target_id=target_id,
                reason="Target not on battlefield",
            )

        if self._is_illegal_attachment(source, target):
            return AttachResult(
                success=False,
                object_id=source_id,
                target_id=target_id,
                reason="Illegal attachment (protection/hexproof/shroud)",
            )

        source.attached_to = target_id
        return AttachResult(success=True, object_id=source_id, target_id=target_id)

    def detach(self, source_id: str) -> AttachResult:
        """Detach an object from its target."""
        source = self._objects.get(source_id)
        if not source:
            return AttachResult(success=False, object_id=source_id, reason="Source not found")

        if not source.attached_to:
            return AttachResult(success=True, object_id=source_id, detached=False)

        source.attached_to = None
        return AttachResult(success=True, object_id=source_id, detached=True)

    def get_attachments(self, obj_id: str) -> List["GameObject"]:
        """Get all objects attached to a target."""
        return [
            obj
            for obj in self._objects.values()
            if obj.attached_to == obj_id and obj.zone == ZONE_BATTLEFIELD
        ]

    def get_attached_to(self, source_id: str) -> Optional["GameObject"]:
        """Get the object that source is attached to."""
        source = self._objects.get(source_id)
        if not source or not source.attached_to:
            return None
        return self._objects.get(source.attached_to)

    def check_legality(self, attachment: "GameObject") -> bool:
        """Check if an attachment is legal. Returns True if legal."""
        if attachment.zone != ZONE_BATTLEFIELD:
            return True  # Not on battlefield, no need to check

        if attachment.phased_out:
            return True  # Phased out, no need to check

        # Check Auras
        if "Aura" in attachment.types:
            if not attachment.attached_to:
                return False

            attached = self._objects.get(attachment.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                return False

            if attached.phased_out:
                return True  # Will phase out with attached permanent

            if self._is_illegal_attachment(attachment, attached):
                return False

            return True

        # Check Equipment
        if "Equipment" in attachment.types:
            if not attachment.attached_to:
                return True  # Unattached equipment is fine

            attached = self._objects.get(attachment.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                return False

            if attached.phased_out:
                return True  # Will phase out with attached permanent

            if "Creature" not in attached.types:
                return False

            return True

        # Generic attachments
        if attachment.attached_to:
            attached = self._objects.get(attachment.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                return False

        return True

    def enforce_legality(self, obj: "GameObject") -> bool:
        """Enforce attachment legality for an object.

        Returns True if the object was moved to graveyard or had attachment detached.
        """
        if obj.zone != ZONE_BATTLEFIELD:
            return False

        if obj.phased_out:
            return False

        # Handle Auras
        if "Aura" in obj.types:
            if not obj.attached_to:
                self._move_object(obj.id, ZONE_GRAVEYARD)
                return True

            attached = self._objects.get(obj.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                obj.attached_to = None
                self._move_object(obj.id, ZONE_GRAVEYARD)
                return True

            if attached.phased_out:
                obj.phased_out = True
                return False

            if self._is_illegal_attachment(obj, attached):
                obj.attached_to = None
                self._move_object(obj.id, ZONE_GRAVEYARD)
                return True

            return False

        # Handle Equipment
        if "Equipment" in obj.types:
            if not obj.attached_to:
                return False

            attached = self._objects.get(obj.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                obj.attached_to = None
                return False

            if attached.phased_out:
                obj.phased_out = True
                return False

            if "Creature" not in attached.types:
                obj.attached_to = None
                return False

            return False

        # Generic attachments
        if obj.attached_to:
            attached = self._objects.get(obj.attached_to)
            if not attached or attached.zone != ZONE_BATTLEFIELD:
                obj.attached_to = None
                return False

            if attached.phased_out:
                obj.phased_out = True

        return False

    def detach_all_from(self, obj_id: str, move_auras_to_graveyard: bool = True) -> List[str]:
        """Detach all objects attached to a target.

        Returns list of detached object IDs.
        """
        detached = []
        for attached in list(self._objects.values()):
            if attached.zone != ZONE_BATTLEFIELD:
                continue
            if attached.attached_to != obj_id:
                continue

            attached.attached_to = None
            detached.append(attached.id)

            if move_auras_to_graveyard and "Aura" in attached.types:
                self._move_object(attached.id, ZONE_GRAVEYARD)

        return detached

    def _is_illegal_attachment(self, attachment: "GameObject", attached: "GameObject") -> bool:
        """Check if an attachment is illegal due to protection/hexproof/shroud."""
        if "Shroud" in attached.keywords:
            return True

        if "Hexproof" in attached.keywords and attachment.controller_id != attached.controller_id:
            return True

        if attached.protections and attachment.colors:
            if any(color in attached.protections for color in attachment.colors):
                return True

        return False
