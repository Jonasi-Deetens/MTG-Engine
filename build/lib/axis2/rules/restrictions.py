import re
from typing import List

from axis1.schema import Axis1Card
from axis2.schema import RestrictionRules
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
# Oracle-text-based restrictions
# ------------------------------------------------------------

def _derive_oracle_restrictions(axis1_card: Axis1Card) -> List[str]:
    """
    Detect restrictions directly from oracle text.
    Examples:
      - "Cast this spell only during your turn."
      - "Cast this spell only if you control a creature."
      - "Cast this spell only during combat."
      - "Cast this spell only before blockers are declared."
    """

    text = _oracle_text(axis1_card)
    restrictions = []

    # Turn-based restrictions
    if "cast this spell only during your turn" in text:
        restrictions.append("cast_only_during_your_turn")

    if "cast this spell only during an opponent's turn" in text:
        restrictions.append("cast_only_during_opponents_turn")

    # Phase-based restrictions
    if "cast this spell only during combat" in text:
        restrictions.append("cast_only_during_combat")

    if "cast this spell only before blockers are declared" in text:
        restrictions.append("cast_only_before_blockers")

    # Condition-based restrictions
    if "cast this spell only if you control a creature" in text:
        restrictions.append("cast_only_if_you_control_creature")

    if "cast this spell only if you control an artifact" in text:
        restrictions.append("cast_only_if_you_control_artifact")

    if "cast this spell only if an opponent was dealt damage" in text:
        restrictions.append("cast_only_if_opponent_damaged")

    # Zone-based restrictions
    if "cast this spell only from your graveyard" in text:
        restrictions.append("cast_only_from_graveyard")

    if "cast this spell only from exile" in text:
        restrictions.append("cast_only_from_exile")

        # Sorcery-speed activation
    if "activate only as a sorcery" in text:
        restrictions.append("activate_only_as_sorcery")

    # Activate only during your turn
    if "activate only during your turn" in text:
        restrictions.append("activate_only_during_your_turn")

    # Activate only once each turn
    if "activate only once each turn" in text:
        restrictions.append("activate_only_once_each_turn")

    # Opponent upkeep
    if "cast this spell only during an opponent's upkeep" in text:
        restrictions.append("cast_only_during_opponents_upkeep")

    # Your upkeep
    if "cast this spell only during your upkeep" in text:
        restrictions.append("cast_only_during_your_upkeep")

    # Before attackers
    if "cast this spell only before attackers are declared" in text:
        restrictions.append("cast_only_before_attackers")

    # Daybound/nightbound
    if "cast this spell only if it's night" in text:
        restrictions.append("cast_only_if_night")
    if "cast this spell only if it's day" in text:
        restrictions.append("cast_only_if_day")

    # Attacked this turn
    if "cast this spell only if you attacked this turn" in text:
        restrictions.append("cast_only_if_you_attacked")

    # Gained life this turn
    if "cast this spell only if you gained life this turn" in text:
        restrictions.append("cast_only_if_you_gained_life")

    # Legendary sorcery
    if "cast this spell only if you control a legendary creature" in text:
        restrictions.append("cast_only_if_control_legendary_creature")

    # Commander requirement
    if "cast this spell only if you control your commander" in text:
        restrictions.append("cast_only_if_control_commander")

    # Hand size conditions
    if "cast this spell only if you have exactly seven cards in hand" in text:
        restrictions.append("cast_only_if_hand_size_7")

    if "cast this spell only if you have no cards in hand" in text:
        restrictions.append("cast_only_if_hand_empty")

    # Opponent land count
    if "cast this spell only if an opponent controls more lands than you" in text:
        restrictions.append("cast_only_if_opponent_more_lands")

    # Control multiple creatures
    if "cast this spell only if you control two or more creatures" in text:
        restrictions.append("cast_only_if_control_two_or_more_creatures")


    return restrictions


# ------------------------------------------------------------
# Global restrictions (Rule of Law, Silence, etc.)
# ------------------------------------------------------------

def _derive_global_restrictions(axis1_card: Axis1Card, game_state: "GameState") -> List[str]:
    """
    Convert global effects into per-card restrictions.
    Examples:
      - "Players can cast only one spell each turn."
      - "Players can't cast spells."
      - "Your opponents can't cast spells."
      - "Players can cast spells only any time they could cast a sorcery."
    """

    restrictions = []

    for effect in game_state.global_restrictions:
        applies_to = effect.get("applies_to", "")
        rule = effect.get("restriction", "")

        # Silence-like effects
        if rule == "players_cannot_cast_spells":
            restrictions.append("cannot_cast_spells")

        if rule == "opponents_cannot_cast_spells" and applies_to == "opponents":
            restrictions.append("opponents_cannot_cast_spells")

        # Rule of Law
        if rule == "one_spell_per_turn":
            restrictions.append("limit_one_spell_per_turn")

        # Sorcery-speed enforcement
        if rule == "cast_only_sorcery_speed":
            restrictions.append("cast_only_sorcery_speed")

    return restrictions


# ------------------------------------------------------------
# Continuous-effect-based restrictions
# ------------------------------------------------------------

def _derive_continuous_restrictions(axis1_card: Axis1Card, game_state: "GameState") -> List[str]:
    """
    Detect restrictions from continuous effects.
    Examples:
      - "Creatures can't attack."
      - "Players can't activate abilities."
      - "Spells can't be countered." (not a restriction, but affects casting)
    """

    restrictions = []

    for effect in game_state.continuous_effects:
        etype = effect.get("type", "")
        applies_to = effect.get("applies_to", "")

        # Ability activation restrictions
        if etype == "cannot_activate_abilities":
            restrictions.append("cannot_activate_abilities")

        # Casting restrictions
        if etype == "cannot_cast_spells":
            restrictions.append("cannot_cast_spells")

        # Creature-specific restrictions
        if etype == "creatures_cannot_attack":
            if "Creature" in axis1_card.characteristics.card_types:
                restrictions.append("creature_cannot_attack")

        if etype == "creatures_cannot_block":
            if "Creature" in axis1_card.characteristics.card_types:
                restrictions.append("creature_cannot_block")

    return restrictions


# ------------------------------------------------------------
# Main restriction derivation
# ------------------------------------------------------------

def derive_restrictions(axis1_card: Axis1Card, game_state: "GameState") -> RestrictionRules:
    """
    Fully derive all restrictions for casting or activating this card.
    """

    restrictions = []

    # 1. Oracle text restrictions
    restrictions.extend(_derive_oracle_restrictions(axis1_card))

    # 2. Global restrictions (Rule of Law, Silence, etc.)
    restrictions.extend(_derive_global_restrictions(axis1_card, game_state))

    # 3. Continuous-effect-based restrictions
    restrictions.extend(_derive_continuous_restrictions(axis1_card, game_state))

    # 4. Deduplicate
    restrictions = list(dict.fromkeys(restrictions))

    return RestrictionRules(restrictions=restrictions)
