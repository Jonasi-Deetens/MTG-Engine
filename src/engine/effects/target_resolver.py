"""Target resolution for effects."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..state import GameObject, GameState, ResolveContext

logger = logging.getLogger(__name__)


@dataclass
class TargetRequirements:
    """Requirements for validating targets."""

    min_targets: int = 0
    max_targets: Optional[int] = None
    target_type: Optional[str] = None
    required_keys: Optional[List[str]] = None
    distinct: bool = False


@dataclass
class ResolvedTargets:
    """Result of target resolution."""

    object_ids: List[str]
    player_ids: List[int]
    valid: bool
    reason: Optional[str] = None


class TargetResolver:
    """Resolves and validates targets for effects.

    Responsible for:
    - Resolving target specifications to object/player IDs
    - Validating targets meet requirements
    - Handling "you_control", "opponents_control" patterns
    - Handling effect-specific targets
    """

    def __init__(self, game_state: "GameState") -> None:
        self._game_state = game_state

    def resolve_targets(
        self,
        effect: Dict[str, Any],
        context: "ResolveContext",
        target_key: Optional[str] = None,
    ) -> List[str]:
        """Resolve targets for an effect.

        Returns a list of object IDs that are valid targets.
        """
        from ..effects_helpers import resolve_target_objects

        # Use the existing helper function for now
        return resolve_target_objects(self._game_state, effect, context)

    def resolve_single(
        self,
        context: "ResolveContext",
        target_key: str,
        fallback_id: Optional[str] = None,
    ) -> Optional["GameObject"]:
        """Resolve a single target object.

        Args:
            context: The resolve context
            target_key: The key to look up in targets
            fallback_id: Fallback object ID if target not found

        Returns:
            The resolved GameObject or None
        """
        from ..targets import resolve_object

        return resolve_object(self._game_state, context, target_key, fallback_id)

    def resolve_player(
        self,
        context: "ResolveContext",
        default_player_id: Optional[int] = None,
    ) -> Optional[int]:
        """Resolve a target player ID."""
        from ..targets import resolve_player_id

        return resolve_player_id(context, default_player_id)

    def resolve_players(
        self,
        effect: Dict[str, Any],
        context: "ResolveContext",
    ) -> List[int]:
        """Resolve multiple target players."""
        from ..effects_helpers import resolve_effect_players

        return resolve_effect_players(self._game_state, effect, context)

    def validate_targets(
        self,
        targets: List[str],
        requirements: TargetRequirements,
        context: "ResolveContext",
    ) -> bool:
        """Validate that targets meet requirements.

        Returns True if all requirements are met.
        """
        # Check count requirements
        if len(targets) < requirements.min_targets:
            return False
        if requirements.max_targets is not None and len(targets) > requirements.max_targets:
            return False

        # Check distinctness
        if requirements.distinct and len(targets) != len(set(targets)):
            return False

        # Check type requirements
        if requirements.target_type:
            for obj_id in targets:
                obj = self._game_state.objects.get(obj_id)
                if not obj:
                    return False
                if requirements.target_type not in obj.types:
                    return False

        return True

    def get_legal_targets(
        self,
        effect: Dict[str, Any],
        context: "ResolveContext",
        target_type: Optional[str] = None,
    ) -> List[str]:
        """Get all legal targets for an effect.

        Returns a list of object IDs that can be legally targeted.
        """
        from ..targets import get_legal_targets

        return get_legal_targets(self._game_state, effect, context)

    def check_target_legality(
        self,
        target_id: str,
        effect: Dict[str, Any],
        context: "ResolveContext",
    ) -> bool:
        """Check if a specific target is legal.

        Returns True if the target is legal.
        """
        obj = self._game_state.objects.get(target_id)
        if not obj:
            return False

        # Check hexproof/shroud
        if "Shroud" in obj.keywords:
            return False
        if "Hexproof" in obj.keywords:
            source = self._game_state.objects.get(context.source_id)
            if source and source.controller_id != obj.controller_id:
                return False

        # Check protection
        if obj.protections:
            source = self._game_state.objects.get(context.source_id)
            if source and source.colors:
                for color in source.colors:
                    if color in obj.protections:
                        return False

        return True
