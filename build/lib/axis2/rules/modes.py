import re
from axis2.schema import Mode
from axis2.rules import targeting as targeting_rules

MODAL_HEADER = re.compile(
    r"choose\s+(one|two|one or more|any number)\s*—",
    re.IGNORECASE
)

def parse_modes(oracle_text: str, game_state):
    """
    Returns (mode_choice, modes) or (None, []) if not modal.
    """
    if not oracle_text:
        return None, []

    m = MODAL_HEADER.search(oracle_text)
    if not m:
        return None, []

    mode_choice = m.group(1).lower()

    # Split modes by bullet or dash
    parts = re.split(r"•|- ", oracle_text)
    mode_texts = [p.strip() for p in parts[1:] if p.strip()]

    modes = []
    for text in mode_texts:
        targeting = targeting_rules.derive_targeting_from_text(text, game_state)
        modes.append(Mode(text=text, targeting=targeting))

    return mode_choice, modes
