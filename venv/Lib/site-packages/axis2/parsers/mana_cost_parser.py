from axis3.rules.costs.mana import ManaCost
import re

MANA_SYMBOL = re.compile(r"\{([^}]+)\}")

def parse_mana_cost(raw_cost: str) -> ManaCost:
    """
    Converts a string like "{1}{G}{G}" into ManaCost(colorless=1, colored={"G": 2})
    """
    if not raw_cost:
        return ManaCost()

    symbols = MANA_SYMBOL.findall(raw_cost)

    colorless = 0
    colored = {}

    for sym in symbols:
        if sym.isdigit():
            colorless += int(sym)
        else:
            colored[sym] = colored.get(sym, 0) + 1

    return ManaCost(colorless=colorless, colored=colored)
