# axis2/parsing/trigger_filters.py

import re
from axis2.schema import TriggerFilter

NONCREATURE_RE = re.compile(r"noncreature spell", re.IGNORECASE)
YOU_RE = re.compile(r"you cast", re.IGNORECASE)
OPPONENT_RE = re.compile(r"opponent casts", re.IGNORECASE)
ANY_PLAYER_RE = re.compile(r"a player casts", re.IGNORECASE)

def parse_trigger_filter(condition_text: str) -> TriggerFilter | None:
    """
    Converts English trigger conditions into structured filters.
    Handles the most common patterns.
    """

    text = condition_text.lower()

    # Start with an empty filter
    f = TriggerFilter()

    # Who?
    if YOU_RE.search(text):
        f.controller_scope = "you"
    elif OPPONENT_RE.search(text):
        f.controller_scope = "opponent"
    elif ANY_PLAYER_RE.search(text):
        f.controller_scope = "any_player"

    # Spell type restrictions
    if NONCREATURE_RE.search(text):
        f.spell_must_not_have_types.append("Creature")

    # If nothing was detected, return None
    if (
        not f.spell_must_have_types
        and not f.spell_must_not_have_types
        and f.controller_scope is None
    ):
        return None

    return f
