from axis1.schema import Axis1Card
from axis2.schema import CostRules
from typing import TYPE_CHECKING
if TYPE_CHECKING: 
    from axis2.builder import GameState
import re

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _parse_kicker(axis1_card: Axis1Card) -> list:
    """
    Detect kicker costs from oracle text.
    Example:
        "Kicker {2}{G}"
        "Multikicker {1}{U}"
    """
    text = (axis1_card.faces[0].oracle_text or "").lower()
    costs = []

    if "kicker" in text:
        # Very simple extraction for now
        # TODO: implement full regex-based parsing
        parts = text.split("kicker")
        for part in parts[1:]:
            if "{" in part:
                cost = part.split("}")[0] + "}"
                costs.append(cost.strip())

    return costs


def _parse_cycling(axis1_card: Axis1Card) -> list:
    """
    Detect cycling costs.
    Example:
        "Cycling {2}"
        "Basic landcycling {G}"
    """
    text = (axis1_card.faces[0].oracle_text or "").lower()
    costs = []

    if "cycling" in text:
        parts = text.split("cycling")
        for part in parts[1:]:
            if "{" in part:
                cost = part.split("}")[0] + "}"
                costs.append(cost.strip())

    return costs


def _parse_evoke(axis1_card: Axis1Card) -> list:
    """
    Detect evoke costs.
    Example:
        "Evoke {1}{G}"
    """
    text = (axis1_card.faces[0].oracle_text or "").lower()
    costs = []

    if "evoke" in text:
        parts = text.split("evoke")
        for part in parts[1:]:
            if "{" in part:
                cost = part.split("}")[0] + "}"
                costs.append(cost.strip())

    return costs


def _parse_overload(axis1_card: Axis1Card) -> list:
    """
    Detect overload costs.
    Example:
        "Overload {3}{U}{U}"
    """
    text = (axis1_card.faces[0].oracle_text or "").lower()
    costs = []

    if "overload" in text:
        parts = text.split("overload")
        for part in parts[1:]:
            if "{" in part:
                cost = part.split("}")[0] + "}"
                costs.append(cost.strip())

    return costs


def _parse_escape(axis1_card: Axis1Card) -> list:
    """
    Detect escape costs.
    Example:
        "Escape—{4}{G}, Exile two other cards from your graveyard."
    """
    text = (axis1_card.faces[0].oracle_text or "").lower()
    costs = []

    if "escape" in text:
        parts = text.split("escape")
        for part in parts[1:]:
            if "{" in part:
                cost = part.split("}")[0] + "}"
                costs.append(cost.strip())

    return costs


def _parse_prototype(axis1_card: Axis1Card) -> list:
    """
    Detect prototype alternative costs.
    Example:
        "Prototype {2}{G} — 2/2"
    """
    text = (axis1_card.faces[0].oracle_text or "").lower()
    costs = []

    if "prototype" in text:
        parts = text.split("prototype")
        for part in parts[1:]:
            if "{" in part:
                cost = part.split("}")[0] + "}"
                costs.append(cost.strip())

    return costs

ADDITIONAL_COST_PATTERN = re.compile(
    r"As an additional cost to cast this spell, (?P<cost>.+?)(?:\.|\n|$)",
    re.IGNORECASE,
)

def _parse_additional_costs(axis1_card: Axis1Card) -> list:
    text = axis1_card.faces[0].oracle_text or ""
    matches = ADDITIONAL_COST_PATTERN.findall(text)
    return [m.strip() for m in matches]

COST_REDUCTION_PATTERN = re.compile(
    r"This spell costs (?P<amount>\{[^}]+\}) less to cast for each (?P<condition>.+?)(?:\.|\n|$)",
    re.IGNORECASE,
)

def _parse_cost_reductions(axis1_card: Axis1Card) -> list:
    text = axis1_card.faces[0].oracle_text or ""
    reductions = []
    for m in COST_REDUCTION_PATTERN.finditer(text):
        reductions.append({
            "amount": m.group("amount"),
            "condition": m.group("condition").strip(),
        })
    return reductions

def _apply_cost_reductions(axis1_card: Axis1Card, game_state: "GameState", reductions: list):
    """
    Apply continuous effects that reduce costs.
    Examples:
        "Creature spells you cast cost {1} less"
        "Instant and sorcery spells you cast cost {1} less"
        "This spell costs {X} less to cast"
    """
    for effect in game_state.continuous_effects:
        etype = effect.get("type", "")
        applies_to = effect.get("applies_to", "")
        amount = effect.get("amount", "")

        # Global reduction
        if etype == "cost_reduction" and applies_to == "all_spells":
            reductions.append(amount)

        # Creature spells cost less
        if etype == "cost_reduction" and applies_to == "creature_spells":
            if "Creature" in axis1_card.characteristics.card_types:
                reductions.append(amount)

        # Noncreature spells cost less
        if etype == "cost_reduction" and applies_to == "noncreature_spells":
            if "Creature" not in axis1_card.characteristics.card_types:
                reductions.append(amount)

        # Specific card reduction
        if etype == "cost_reduction" and applies_to == axis1_card.card_id:
            reductions.append(amount)


def _apply_cost_increases(axis1_card: Axis1Card, game_state: "GameState", increases: list):
    """
    Apply continuous effects that increase costs.
    Examples:
        "Spells your opponents cast cost {1} more"
        "This spell costs {2} more to cast"
    """
    for effect in game_state.continuous_effects:
        etype = effect.get("type", "")
        applies_to = effect.get("applies_to", "")
        amount = effect.get("amount", "")

        if etype == "cost_increase":
            # Global increase
            if applies_to == "all_spells":
                increases.append(amount)

            # Creature spells cost more
            if applies_to == "creature_spells" and "Creature" in axis1_card.characteristics.card_types:
                increases.append(amount)

            # Specific card
            if applies_to == axis1_card.card_id:
                increases.append(amount)


def _apply_commander_tax(axis1_card: Axis1Card, game_state: "GameState", increases: list):
    """
    Apply commander tax:
        +{2} for each time the commander has been cast from the command zone.
    """
    if not getattr(axis1_card, "is_commander", False):
        return

    casts = game_state.command_zone.count(axis1_card.card_id)
    if casts > 0:
        increases.append(f"+{2 * casts}")


# ------------------------------------------------------------
# Main cost derivation
# ------------------------------------------------------------

def derive_cost(axis1_card: Axis1Card, game_state: "GameState") -> CostRules:
    """
    Fully derive the cost structure for a spell or ability.
    """

    base_cost = axis1_card.characteristics.mana_cost

    additional = []
    alternative = []
    reductions = []
    increases = []

    # ------------------------------------------------------------
    # Keyword-based alternative costs
    # ------------------------------------------------------------
    alternative.extend(_parse_kicker(axis1_card))
    alternative.extend(_parse_evoke(axis1_card))
    alternative.extend(_parse_overload(axis1_card))
    alternative.extend(_parse_escape(axis1_card))
    alternative.extend(_parse_prototype(axis1_card))
    alternative.extend(_parse_cycling(axis1_card))
    additional.extend(_parse_additional_costs(axis1_card))
    reductions.extend(_parse_cost_reductions(axis1_card))

    # ------------------------------------------------------------
    # Continuous effects modifying costs
    # ------------------------------------------------------------
    _apply_cost_reductions(axis1_card, game_state, reductions)
    _apply_cost_increases(axis1_card, game_state, increases)

    # ------------------------------------------------------------
    # Commander tax
    # ------------------------------------------------------------
    _apply_commander_tax(axis1_card, game_state, increases)

    # ------------------------------------------------------------
    # Return full cost structure
    # ------------------------------------------------------------
    return CostRules(
        mana=base_cost,
        additional=additional,
        alternative=alternative,
        reductions=reductions,
        increases=increases,
    )
