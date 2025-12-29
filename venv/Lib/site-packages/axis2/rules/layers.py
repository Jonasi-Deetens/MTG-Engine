from copy import deepcopy
from axis1.schema import Axis1Card
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from axis2.builder import GameState


def apply_layers(axis1_card: Axis1Card, game_state: "GameState") -> Axis1Card:
    """
    Minimal Axis 2 implementation of MTG's 7-layer system.

    This does NOT implement full CR 613 behavior.
    It provides:
      - A safe, non-crashing layer pipeline
      - Hooks for continuous effects
      - Basic static modifications (P/T buffs, ability adds/removes)
      - A clean object to hand off to Axis 3

    Returns a *new* Axis1Card-like object with modifications applied.
    """

    # Work on a copy so we never mutate Axis1 data
    card = deepcopy(axis1_card)

    # ------------------------------------------------------------
    # LAYER 1 — Copy effects
    # ------------------------------------------------------------
    # Placeholder: Axis 3 will implement copy effects
    # Example: "becomes a copy of target creature"
    # For now, do nothing.

    # ------------------------------------------------------------
    # LAYER 2 — Control-changing effects
    # ------------------------------------------------------------
    # Example: "You control enchanted creature"
    for effect in game_state.continuous_effects:
        if effect.get("type") == "change_control":
            if effect.get("target") == card.card_id:
                card.controller = effect.get("new_controller")

    # ------------------------------------------------------------
    # LAYER 3 — Text-changing effects
    # ------------------------------------------------------------
    # Example: "Replace all instances of 'Forest' with 'Island'"
    for effect in game_state.continuous_effects:
        if effect.get("type") == "text_change":
            old = effect.get("old", "").lower()
            new = effect.get("new", "")
            if old and new:
                face = card.faces[0]
                if face.oracle_text:
                    face.oracle_text = face.oracle_text.replace(old, new)

    # ------------------------------------------------------------
    # LAYER 4 — Type-changing effects
    # ------------------------------------------------------------
    # Example: "CARDNAME becomes a creature"
    for effect in game_state.continuous_effects:
        if effect.get("type") == "add_type":
            card.characteristics.card_types.append(effect.get("value"))

        if effect.get("type") == "remove_type":
            t = effect.get("value")
            if t in card.characteristics.card_types:
                card.characteristics.card_types.remove(t)

    # ------------------------------------------------------------
    # LAYER 5 — Color-changing effects
    # ------------------------------------------------------------
    # Example: "CARDNAME becomes blue"
    for effect in game_state.continuous_effects:
        if effect.get("type") == "set_color":
            card.characteristics.colors = [effect.get("value")]

        if effect.get("type") == "add_color":
            c = effect.get("value")
            if c not in card.characteristics.colors:
                card.characteristics.colors.append(c)

        if effect.get("type") == "remove_color":
            c = effect.get("value")
            if c in card.characteristics.colors:
                card.characteristics.colors.remove(c)

    # ------------------------------------------------------------
    # LAYER 6 — Ability-adding/removing effects
    # ------------------------------------------------------------
    # Example: "CARDNAME gains flying"
    # Example: "CARDNAME loses all abilities"
    face = card.faces[0]

    for effect in game_state.continuous_effects:
        if effect.get("type") == "add_ability":
            ability = effect.get("value")
            if ability not in face.keywords:
                face.keywords.append(ability)

        if effect.get("type") == "remove_ability":
            ability = effect.get("value")
            if ability in face.keywords:
                face.keywords.remove(ability)

        if effect.get("type") == "remove_all_abilities":
            face.keywords = []

    # ------------------------------------------------------------
    # LAYER 7 — Power/Toughness modifications
    # ------------------------------------------------------------
    # Example: "Creatures you control get +1/+1"
    for effect in game_state.continuous_effects:
        if effect.get("type") == "pt_modifier":
            pt = effect.get("value", {})
            card.characteristics.power += pt.get("power", 0)
            card.characteristics.toughness += pt.get("toughness", 0)

        if effect.get("type") == "set_pt":
            pt = effect.get("value", {})
            card.characteristics.power = pt.get("power", card.characteristics.power)
            card.characteristics.toughness = pt.get("toughness", card.characteristics.toughness)

    return card
