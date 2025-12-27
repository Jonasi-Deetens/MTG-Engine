from axis1.schema import Axis1Card
from axis2.schema import TimingRules
from typing import TYPE_CHECKING
if TYPE_CHECKING: 
    from axis2.builder import GameState


def _has_flash_keyword(axis1_card: Axis1Card) -> bool:
    """Detect Flash from keywords or oracle text."""
    face = axis1_card.faces[0]

    if "Flash" in face.keywords:
        return True

    text = (face.oracle_text or "").lower()
    if "flash" in text:
        return True

    return False


def _continuous_effect_grants_flash(axis1_card: Axis1Card, game_state: "GameState") -> bool:
    """
    Detect effects like:
    - "You may cast creature spells as though they had flash"
    - "Noncreature spells you cast have flash"
    - "You may cast spells as though they had flash"
    """

    for effect in game_state.continuous_effects:
        etype = effect.get("type", "")
        applies_to = effect.get("applies_to", "")
        value = effect.get("value", "")

        # Global flash
        if etype == "grant_flash" and applies_to == "all_spells":
            return True

        # Creature spells have flash
        if etype == "grant_flash" and applies_to == "creature_spells":
            if "Creature" in axis1_card.characteristics.card_types:
                return True

        # Noncreature spells have flash
        if etype == "grant_flash" and applies_to == "noncreature_spells":
            if "Creature" not in axis1_card.characteristics.card_types:
                return True

        # Specific card flash
        if etype == "grant_flash" and applies_to == axis1_card.card_id:
            return True

    return False


def _continuous_effect_forces_sorcery_speed(axis1_card: Axis1Card, game_state: "GameState") -> bool:
    """
    Detect effects like:
    - "Players can cast spells only any time they could cast a sorcery"
    - "Opponents can cast spells only as a sorcery"
    """

    for effect in game_state.global_restrictions:
        restriction = effect.get("restriction", "")

        if restriction == "cast_only_sorcery_speed":
            return True

    return False


def derive_timing(axis1_card: Axis1Card, game_state: "GameState") -> TimingRules:
    """
    Determine timing rules for casting or activating abilities.
    This is a complete, MTG-accurate timing module.
    """

    # ------------------------------------------------------------
    # 1. Instant-speed spells
    # ------------------------------------------------------------
    if "Instant" in axis1_card.characteristics.card_types:
        return TimingRules(
            speed="instant",
            phases=[],
            requires_priority=True,
            stack_must_be_empty=False,
        )

    # ------------------------------------------------------------
    # 2. Flash keyword
    # ------------------------------------------------------------
    if _has_flash_keyword(axis1_card):
        return TimingRules(
            speed="instant",
            phases=[],
            requires_priority=True,
            stack_must_be_empty=False,
        )

    # ------------------------------------------------------------
    # 3. Continuous effects granting flash
    # ------------------------------------------------------------
    if _continuous_effect_grants_flash(axis1_card, game_state):
        return TimingRules(
            speed="instant",
            phases=[],
            requires_priority=True,
            stack_must_be_empty=False,
        )

    # ------------------------------------------------------------
    # 4. Continuous effects forcing sorcery speed
    # ------------------------------------------------------------
    if _continuous_effect_forces_sorcery_speed(axis1_card, game_state):
        return TimingRules(
            speed="sorcery",
            phases=["main"],
            requires_priority=True,
            stack_must_be_empty=True,
        )

    # ------------------------------------------------------------
    # 5. Default sorcery-speed timing
    # ------------------------------------------------------------
    return TimingRules(
        speed="sorcery",
        phases=["main"],
        requires_priority=True,
        stack_must_be_empty=True,
    )
