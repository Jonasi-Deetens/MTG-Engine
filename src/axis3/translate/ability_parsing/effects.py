import re

from axis3.engine.abilities.effects.mana import AddManaEffect
from axis3.engine.abilities.effects.damage import DealDamageEffect
from axis3.engine.abilities.effects.draw import DrawCardEffect


# Matches: "Add {W}", "Add {R}{R}", "Add {G}{G}{G}."
MANA_SYMBOL_EFFECT_PATTERN = re.compile(
    r"^add\s+(?P<mana>(?:\{[WUBRG]\})+)\.?$", re.IGNORECASE
)


def parse_target(text: str) -> str:
    """
    Convert English target text into Axis3 subject resolver keys.
    """
    t = text.lower().strip()

    if t == "any target":
        return "any"

    if "target creature" in t:
        return "target_creature"

    if "target player" in t:
        return "target_player"

    if "target opponent" in t:
        return "target_opponent"

    if "each creature" in t:
        return "each_creature"

    if "each opponent" in t:
        return "each_opponent"

    return t  # fallback for unusual patterns


def parse_effect_string(effect_str: str):
    """
    Parse a single effect string into Axis3Effect objects.
    Returns: (effects: List[Axis3Effect], is_mana_ability: bool)
    """

    effect_str = effect_str.strip()
    lower = effect_str.lower()

    # ------------------------------------------------------------
    # 1. Mana abilities: "Add {W}", "Add {R}{R}", etc.
    # ------------------------------------------------------------
    m = MANA_SYMBOL_EFFECT_PATTERN.match(effect_str)
    if m:
        mana_str = m.group("mana").upper()
        effects = []

        for sym in re.findall(r"\{([WUBRG])\}", mana_str):
            effects.append(AddManaEffect(color=sym))

        return effects, True  # mana abilities do not use the stack

    # ------------------------------------------------------------
    # 2. Damage: "Deal 1 damage to any target"
    # ------------------------------------------------------------
    if "damage" in lower:
        m = re.search(r"deal\s+(\d+)\s+damage\s+to\s+(.+)", lower)
        if not m:
            return [], False

        amount = int(m.group(1))
        subject_text = m.group(2).strip()
        subject = parse_target(subject_text)

        return [DealDamageEffect(amount=amount, subject=subject)], False

    # ------------------------------------------------------------
    # 3. Draw cards: "Draw 2 cards"
    # ------------------------------------------------------------
    if lower.startswith("draw"):
        m = re.search(r"draw\s+(\d+)\s+cards?", lower)
        if not m:
            return [], False

        amount = int(m.group(1))
        return [DrawCardEffect(amount=amount)], False

    # ------------------------------------------------------------
    # Default: no effect recognized
    # ------------------------------------------------------------
    return [], False
