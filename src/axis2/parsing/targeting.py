# axis2/parsing/targeting.py

import re
from axis2.schema import TargetingRules

def parse_targeting(text: str):
    """
    Extracts basic targeting rules from effect text.
    Handles:
      - target creature
      - target player
      - target planeswalker
      - target player or planeswalker
      - target creature or planeswalker
      - any target
      - target creature you control
      - target creature an opponent controls
    """
    t = text.lower()
    if "target" not in t:
        return None

    rules = TargetingRules(required=True, min=1, max=1)

    # -----------------------------------------
    # 1. Compound targets (must check first)
    # -----------------------------------------
    if "target player or planeswalker" in t:
        rules.legal_targets = ["player", "planeswalker"]
        return rules

    if "target creature or planeswalker" in t:
        rules.legal_targets = ["creature", "planeswalker"]
        return rules

    # -----------------------------------------
    # 2. Any target
    # -----------------------------------------
    if "any target" in t:
        rules.legal_targets = ["any_target"]
        return rules

    # -----------------------------------------
    # 3. Creature targets
    # -----------------------------------------
    if "target creature you control" in t:
        rules.legal_targets = ["creature"]
        rules.restrictions.append("you_control")
        return rules

    if "target creature an opponent controls" in t:
        rules.legal_targets = ["creature"]
        rules.restrictions.append("opponent_controls")
        return rules

    if "target creature" in t:
        rules.legal_targets = ["creature"]
        return rules

    # -----------------------------------------
    # 4. Player targets
    # -----------------------------------------
    if "target opponent" in t:
        rules.legal_targets = ["player"]
        rules.restrictions.append("opponent")
        return rules

    if "target player" in t:
        rules.legal_targets = ["player"]
        return rules

    # -----------------------------------------
    # 5. Planeswalker targets
    # -----------------------------------------
    if "target planeswalker" in t:
        rules.legal_targets = ["planeswalker"]
        return rules

    # -----------------------------------------
    # 6. Fallback
    # -----------------------------------------
    rules.legal_targets = ["any"]
    return rules
