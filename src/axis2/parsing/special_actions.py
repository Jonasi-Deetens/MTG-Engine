import re
from axis2.schema import SpecialAction, ManaCost

NINJUTSU_RE = re.compile(r"ninjutsu\s+(\{[^}]+\})", re.IGNORECASE)

def parse_ninjutsu(oracle_text: str):
    """
    Detects and parses Ninjutsu keyword into a SpecialAction.
    Example:
        'Ninjutsu {1}{U}' → SpecialAction(...)
    """
    if not oracle_text:
        return None

    m = NINJUTSU_RE.search(oracle_text)
    if not m:
        return None

    cost_text = m.group(1)

    # Parse mana cost symbols
    symbols = []
    buf = ""
    inside = False
    for ch in cost_text:
        if ch == "{":
            inside = True
            buf = "{"
        elif ch == "}":
            inside = False
            buf += "}"
            symbols.append(buf)
            buf = ""
        elif inside:
            buf += ch

    cost = ManaCost(symbols=symbols)

    # Semantic meaning of Ninjutsu
    conditions = [
        "you_control_unblocked_attacker",
        "card_in_hand",
    ]

    effects = [
        {
            "type": "put_onto_battlefield_tapped_and_attacking",
            "subject": "this",
            "origin": "hand",
        }
    ]

    return SpecialAction(
        name="Ninjutsu",
        cost=cost,
        conditions=conditions,
        effects=effects,
    )
