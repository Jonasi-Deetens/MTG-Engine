from axis3.engine.abilities.costs.tap import TapCost
from axis3.rules.costs.mana import ManaCost

def parse_cost_string(cost_str: str):
    cost_str = cost_str.strip()

    # 1. Tap cost
    if cost_str == "{T}":
        return [TapCost()]

    # 2. Mana cost (e.g. {1}{G}{G})
    if cost_str.startswith("{") and "}" in cost_str:
        # Extract symbols like {1}, {G}, {U}, etc.
        symbols = [s for s in cost_str.split("}") if s]
        symbols = [s.replace("{", "") for s in symbols]

        colorless = 0
        colored = {}

        for sym in symbols:
            if sym.isdigit():
                colorless += int(sym)
            else:
                colored[sym] = colored.get(sym, 0) + 1

        return [ManaCost(colorless=colorless, colored=colored)]

    # 3. Sacrifice cost
    if cost_str.lower().startswith("sacrifice"):
        # Later: parse target type
        from axis3.engine.abilities.costs.sacrifice import SacrificeCost
        return [SacrificeCost(cost_str)]

    # 4. Pay life
    if "life" in cost_str.lower():
        from axis3.engine.abilities.costs.pay_life import PayLifeCost
        # naive parse: "Pay 2 life"
        amount = int(cost_str.split()[1])
        return [PayLifeCost(amount)]

    # Default: no cost
    return []
