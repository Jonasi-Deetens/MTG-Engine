from engine.mana import mana_cost_snapshot, parse_mana_cost


def mana_cost_data(cost_text: str) -> dict:
    return mana_cost_snapshot(parse_mana_cost(cost_text))

