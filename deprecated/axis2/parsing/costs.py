# axis2/parsing/costs.py

import re
from typing import List, Optional
from axis2.parsing.mana import parse_mana_cost
from axis2.schema import (
    TapCost,
    SacrificeCost,
    LoyaltyCost,
    ManaCost,
    DiscardCost,
    EscapeCost,
)
from axis2.schema import Subject


# ------------------------------------------------------------
# Regex helpers
# ------------------------------------------------------------

# Match ANY mana/tap/hybrid/phyrexian/snow symbol
MANA_SYMBOL_RE = re.compile(r"\{[^}]+\}")

# Split multi-part costs like "{1}{R}, {T}, Sacrifice this artifact"
COST_SPLIT_RE = re.compile(r",\s*")

# Tap OTHER permanent you control
TAP_OTHER_RE = re.compile(
    r"tap (an|a|one|two)? ?(untapped )?(creature|artifact|permanent)s? you control"
)

# Discard cost
DISCARD_COST_RE = re.compile(r"discard (\w+) cards?", re.IGNORECASE)

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
}


# ------------------------------------------------------------
# Discard cost
# ------------------------------------------------------------

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
        "{1}{R}, {T}, Tap an untapped creature you control"
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
        # 2. Tap OTHER permanent you control
        # --------------------------------------------------------
        m = TAP_OTHER_RE.search(lower)
        if m:
            count_word = m.group(1) or "one"
            untapped = bool(m.group(2))
            type_word = m.group(3)

            # normalize count
            count = 1
            if count_word == "two":
                count = 2

            restrictions = []
            if untapped:
                restrictions.append("untapped")

            costs.append(
                TapCost(
                    amount=count,
                    subject=Subject(scope=f"{type_word}_you_control"),
                    restrictions=restrictions
                )
            )
            continue

        # --------------------------------------------------------
        # 3. Generic tap cost ("Tap this", "Tap this creature")
        # --------------------------------------------------------
        if "{t}" in lower or lower.startswith("tap "):
            costs.append(TapCost(subject=Subject(scope="self")))
            continue

        # --------------------------------------------------------
        # 4. Sacrifice cost
        # --------------------------------------------------------
        if lower.startswith("sacrifice"):
            subject = Subject(scope="self")
            if "artifact" in lower:
                subject.types = ["artifact"]
            costs.append(SacrificeCost(subject=subject))
            continue

        # --------------------------------------------------------
        # 5. Discard cost
        # --------------------------------------------------------
        disc = parse_discard_cost(part)
        if disc:
            costs.append(disc)
            continue

        # --------------------------------------------------------
        # 6. Loyalty cost
        # --------------------------------------------------------
        if lower.startswith("+") or lower.startswith("−") or lower.startswith("-"):
            amount = int(lower.replace("−", "-"))
            costs.append(LoyaltyCost(amount=amount))
            continue

        # --------------------------------------------------------
        # 7. Unknown cost type (future extension)
        # --------------------------------------------------------
        pass

    # Insert mana cost at the front
    if mana_symbols:
        costs.insert(0, ManaCost(symbols=mana_symbols))

    return costs

def parse_escape_cost(text: str) -> Optional[EscapeCost]:
    # Example: "Escape—{W}, Exile two other cards from your graveyard."
    m = re.search(r"escape—([^,]+),\s*exile (\w+) other cards", text, re.IGNORECASE)
    if not m:
        return None

    mana = parse_mana_cost(m.group(1))
    count_word = m.group(2).lower()
    count = NUMBER_WORDS.get(count_word, None)
    if count is None:
        return None

    return EscapeCost(mana_cost=mana, exile_count=count, restriction="other")
