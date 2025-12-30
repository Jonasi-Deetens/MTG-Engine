# axis2/parsing/modes.py

from axis2.schema import Mode
from axis2.parsing.effects import parse_effect_text
from axis2.parsing.targeting import parse_targeting

def parse_modes(oracle_text):
    """
    Very simple modal parser. Expand later.
    """
    if not oracle_text or "choose one" not in oracle_text.lower():
        return None, []

    lines = oracle_text.split("\n")
    modes = []
    for line in lines:
        if line.strip().startswith("•"):
            text = line.strip("• ").strip()
            effects = parse_effect_text(text)
            targeting = parse_targeting(text)
            modes.append(Mode(text=text, effects=effects, targeting=targeting))

    return "choose_one", modes