# src/axis3/abilities/keyword.py

from __future__ import annotations
from typing import Set
from axis3.state.objects import RuntimeObject
from axis3.rules.layers.types import EvaluatedCharacteristics

# Standard keywords we support
KEYWORDS = {
    "flying",
    "vigilance",
    "deathtouch",
    "trample",
    "haste",
    "hexproof",
    "indestructible",
}


def apply_keyword_abilities(game_state: "GameState", rt_obj: RuntimeObject, ec: EvaluatedCharacteristics):
    """
    Applies keyword abilities from the object's characteristics or continuous effects.
    This should be called in Layer 6 (ability adding/removing layer).
    """
    # Start with printed/static keywords
    keywords: Set[str] = set(getattr(rt_obj.characteristics, "abilities", []))

    # Add keywords from continuous effects
    for ce in getattr(game_state, "continuous_effects", []):
        if ce.layer == 6 and ce.grant_abilities and ce.applies_to(game_state, rt_obj.id):
            ce.grant_abilities(game_state, rt_obj.id, keywords)

    # Only keep valid keywords
    keywords.intersection_update(KEYWORDS)

    # Update the evaluated characteristics
    ec.abilities = keywords
    return ec
