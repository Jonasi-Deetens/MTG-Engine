# axis2/parsing/mana.py

from axis2.schema import ManaCost

def parse_mana_cost(mana_cost_str):
    if not mana_cost_str:
        return None
    symbols = []
    buf = ""
    inside = False
    for ch in mana_cost_str:
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
    return ManaCost(symbols=symbols)