# axis2/parsing/costs.py

import re
from axis2.schema import TapCost, SacrificeCost, LoyaltyCost, ManaCost

def parse_cost(axis1_cost_part):
    raw = axis1_cost_part["raw"].lower()

    if raw == "{t}":
        return TapCost()

    if raw.startswith("sacrifice"):
        return SacrificeCost(subject="this")

    if raw.startswith("+") or raw.startswith("−") or raw.startswith("-"):
        # loyalty ability
        return LoyaltyCost(amount=int(raw.replace("−", "-")))

    # fallback: treat as mana cost
    mana_symbols = axis1_cost_part["metadata"]["mana_cost_symbols"]
    return ManaCost(symbols=mana_symbols)

TAP_COST_RE = re.compile(
    r"tap (\w+) ([a-z ]+?) you control",
    re.IGNORECASE
)

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
}

def parse_number(word: str):
    word = word.lower()
    if word.isdigit():
        return int(word)
    if word in NUMBER_WORDS:
        return NUMBER_WORDS[word]
    if word == "a" or word == "an":
        return 1
    return 1

def parse_tap_cost(text: str):
    m = TAP_COST_RE.search(text)
    if not m:
        return None

    amount_word = m.group(1)
    restrictions_raw = m.group(2).strip().lower()

    amount = parse_number(amount_word)

    restrictions = ["you_control"]

    parts = restrictions_raw.split()
    for p in parts:
        if p == "untapped":
            restrictions.append("untapped")
        elif p == "artifact":
            restrictions.append("artifact")
        elif p == "creature":
            restrictions.append("creature")
        # add more as needed

    return TapCost(amount=amount, restrictions=restrictions)
