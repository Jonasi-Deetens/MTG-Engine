import re
from typing import List

from axis1.schema import Axis1Card
from axis2.schema import PermissionRules
from typing import TYPE_CHECKING
if TYPE_CHECKING: 
    from axis2.builder import GameState


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _oracle_text(axis1_card: Axis1Card) -> str:
    face = axis1_card.faces[0]
    return (face.oracle_text or "").strip().lower()


def _has_phrase(text: str, phrase: str) -> bool:
    return phrase in text


def _regex(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


# ------------------------------------------------------------
# Oracle-text-based permissions
# ------------------------------------------------------------

def _derive_oracle_zone_permissions(axis1_card: Axis1Card) -> List[str]:
    """
    Zone-based permissions from oracle text:
      - "You may cast this card from your graveyard"
      - "You may cast CARDNAME from exile"
      - "You may play lands from your graveyard"
      - "You may play an additional land on each of your turns"
    """

    text = _oracle_text(axis1_card)
    permissions: List[str] = []

    # Cast from graveyard
    if _has_phrase(text, "you may cast this card from your graveyard") or \
       _has_phrase(text, "you may cast this spell from your graveyard"):
        permissions.append("may_cast_from_graveyard")

    # Cast from exile
    if _has_phrase(text, "you may cast this card from exile") or \
       _has_phrase(text, "you may cast this spell from exile"):
        permissions.append("may_cast_from_exile")

    # Cast from command zone
    if _has_phrase(text, "you may cast this card from the command zone") or \
       _has_phrase(text, "you may cast this spell from the command zone"):
        permissions.append("may_cast_from_command")

    # Play lands from graveyard
    if _has_phrase(text, "you may play lands from your graveyard"):
        permissions.append("may_play_lands_from_graveyard")

    # Additional land plays
    if _has_phrase(text, "you may play an additional land") or \
       _has_phrase(text, "you may play an additional land on each of your turns"):
        permissions.append("may_play_additional_land_per_turn")

    return permissions


def _derive_keyword_permissions(axis1_card: Axis1Card) -> List[str]:
    """
    Keyword-based permissions from mechanics like:
      - flashback
      - escape
      - retrace
      - jump-start
      - adventure
      - foretell
      - unearth (cast/activate from graveyard)
    """

    text = _oracle_text(axis1_card)
    permissions: List[str] = []

    if "flashback" in text:
        permissions.append("has_flashback")
        permissions.append("may_cast_from_graveyard")

    if "escape" in text:
        permissions.append("has_escape")
        permissions.append("may_cast_from_graveyard")

    if "retrace" in text:
        permissions.append("has_retrace")
        permissions.append("may_cast_from_graveyard")

    if "jump-start" in text:
        permissions.append("has_jump_start")
        permissions.append("may_cast_from_graveyard")

    if "foretell" in text:
        permissions.append("has_foretell")
        # actual foretell permission is more complex, but we mark it here

    if "adventure" in text:
        permissions.append("has_adventure")

    if "unearth" in text:
        permissions.append("has_unearth")
        permissions.append("may_activate_from_graveyard")

    return permissions


# ------------------------------------------------------------
# Continuous-effect-based permissions
# ------------------------------------------------------------

def _derive_continuous_permissions(axis1_card: Axis1Card, game_state: "GameState") -> List[str]:
    """
    Permissions granted by global/continuous effects:
      - "You may play lands from your graveyard."
      - "You may play an additional land on each of your turns."
      - "You may cast spells as though they had flash." (timing hook, but also a permission)
    """

    permissions: List[str] = []

    for effect in game_state.continuous_effects:
        etype = effect.get("type", "")
        applies_to = effect.get("applies_to", "")

        # Extra land plays
        if etype == "extra_land_play":
            permissions.append("may_play_additional_land_per_turn")

        # Play lands from graveyard
        if etype == "play_lands_from_graveyard":
            permissions.append("may_play_lands_from_graveyard")

        # Cast from graveyard generically
        if etype == "cast_from_graveyard":
            # could be scoped to specific cards/types later
            permissions.append("may_cast_from_graveyard")

        # Flash-like permission (overlaps timing, but we mark it here)
        if etype == "cast_as_though_had_flash":
            permissions.append("may_cast_as_though_had_flash")

    return permissions


# ------------------------------------------------------------
# Main permission derivation
# ------------------------------------------------------------

def derive_permissions(axis1_card: Axis1Card, game_state: "GameState") -> PermissionRules:
    """
    Fully derive permissions for this card:
      - where and when it can be cast/played
      - extra land permissions
      - special keyword mechanics like flashback/escape/retrace/jump-start
    """

    permissions: List[str] = []

    # 1. Oracle text (explicit zone/land permissions)
    permissions.extend(_derive_oracle_zone_permissions(axis1_card))

    # 2. Keyword-based (flashback, escape, retrace, etc.)
    permissions.extend(_derive_keyword_permissions(axis1_card))

    # 3. Continuous effects (global permissions)
    permissions.extend(_derive_continuous_permissions(axis1_card, game_state))

    # 4. Deduplicate
    permissions = list(dict.fromkeys(permissions))

    return PermissionRules(permissions=permissions)
