from axis3.engine.abilities.effects.mana import AddManaEffect
from axis3.engine.abilities.effects.damage import DealDamageEffect
from axis3.engine.abilities.effects.draw import DrawCardEffect
import re

MANA_SYMBOL_EFFECT_PATTERN = re.compile(
    r"^add\s+(?P<mana>(?:\{[WUBRG]\})+)\.?$", re.IGNORECASE
)

def parse_effect_string(effect_str: str):
    raw = effect_str
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
            effects.append(
                AddManaEffect(
                    selector="add_mana",
                    subject="controller",
                    params={"color": sym},
                    raw=raw,
                )
            )

        return effects, True

    # ------------------------------------------------------------
    # 2. Damage: "Deal 1 damage to any target"
    # ------------------------------------------------------------
    if "damage" in lower:
        parts = effect_str.split()
        try:
            amount = int(parts[1])
        except Exception:
            return [], False

        return [
            DealDamageEffect(
                selector="deal_damage",
                subject="target",
                params={"amount": amount},
                raw=raw,
            )
        ], False

    # ------------------------------------------------------------
    # 3. Draw cards: "Draw 2 cards"
    # ------------------------------------------------------------
    if lower.startswith("draw"):
        parts = effect_str.split()
        try:
            amount = int(parts[1])
        except Exception:
            return [], False

        return [
            DrawCardEffect(
                selector="draw",
                subject="controller",
                params={"amount": amount},
                raw=raw,
            )
        ], False

    # ------------------------------------------------------------
    # Default: no effect
    # ------------------------------------------------------------
    return [], False
