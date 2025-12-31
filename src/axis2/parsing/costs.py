# axis2/parsing/costs.py

import re
from typing import List
from axis2.schema import (
    TapCost,
    SacrificeCost,
    LoyaltyCost,
    ManaCost,
    DiscardCost,
)
from axis2.schema import Subject


# ------------------------------------------------------------
# Regex helpers
# ------------------------------------------------------------

# Match ANY mana/tap/hybrid/phyrexian/snow symbol
MANA_SYMBOL_RE = re.compile(r"\{[^}]+\}")

# Split multi-part costs like "{1}{R}, {T}, Sacrifice this artifact"
COST_SPLIT_RE = re.compile(r",\s*")


# ------------------------------------------------------------
# Discard cost
# ------------------------------------------------------------

DISCARD_COST_RE = re.compile(r"discard (\w+) cards?", re.IGNORECASE)

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
}

def parse_discard_cost(text: str):
    m = DISCARD_COST_RE.search(text)
    if not m:
        return None

    raw = m.group(1).lower()

    if raw.isdigit():
        amount = int(raw)
    else:
        amount = NUMBER_WORDS.get(raw)

    if amount is None:
        return None

    return DiscardCost(amount=amount)


# ------------------------------------------------------------
# Main multi-part cost parser
# ------------------------------------------------------------

def parse_cost_string(cost_text: str) -> List:
    """
    Parses cost text like:
        "{1}{R}, {T}, Sacrifice this artifact"
    into a list of Cost objects.
    """
    parts = [p.strip() for p in COST_SPLIT_RE.split(cost_text) if p.strip()]
    costs = []
    mana_symbols = []

    for part in parts:
        lower = part.lower()

        # --------------------------------------------------------
        # 1. Mana symbols (including hybrid, phyrexian, snow, etc.)
        # --------------------------------------------------------
        if part.startswith("{"):
            syms = MANA_SYMBOL_RE.findall(part)
            for sym in syms:
                if sym.upper() == "{T}":
                    # Tap is not mana
                    costs.append(TapCost(subject=Subject(scope="self")))
                else:
                    mana_symbols.append(sym)
            continue

        # --------------------------------------------------------
        # 2. Tap cost ("{T}" or "Tap this creature")
        # --------------------------------------------------------
        if "{t}" in lower or lower.startswith("tap "):
            costs.append(TapCost(subject=Subject(scope="self")))
            continue

        # --------------------------------------------------------
        # 3. Sacrifice cost
        # --------------------------------------------------------
        if lower.startswith("sacrifice"):
            # "Sacrifice this artifact" → Subject(scope="self", types=["artifact"])
            subject = Subject(scope="self")
            if "artifact" in lower:
                subject.types = ["artifact"]
            costs.append(SacrificeCost(subject=subject))
            continue

        # --------------------------------------------------------
        # 4. Discard cost
        # --------------------------------------------------------
        disc = parse_discard_cost(part)
        if disc:
            costs.append(disc)
            continue

        # --------------------------------------------------------
        # 5. Loyalty cost
        # --------------------------------------------------------
        if lower.startswith("+") or lower.startswith("−") or lower.startswith("-"):
            amount = int(lower.replace("−", "-"))
            costs.append(LoyaltyCost(amount=amount))
            continue

        # --------------------------------------------------------
        # 6. Unknown cost type (future extension)
        # --------------------------------------------------------
        pass

    # Insert mana cost at the front
    if mana_symbols:
        costs.insert(0, ManaCost(symbols=mana_symbols))

    return costs
