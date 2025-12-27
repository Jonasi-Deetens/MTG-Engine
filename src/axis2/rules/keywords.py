import re
from axis1.schema import Axis1Card
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from axis2.builder import GameState

KEYWORD_ABILITIES = [
    "deathtouch", "first strike", "double strike", "flying", "reach",
    "vigilance", "trample", "lifelink", "haste", "hexproof",
    "indestructible", "menace", "ward", "prowess", "convoke"
]

KEYWORD_TRIGGER_MAP = {
    # Mobilize X
    "mobilize": {
        "event": "attacks",
        "condition": "Whenever this creature attacks",
        "effect_template": (
            "create a tapped and attacking 1/1 red Warrior creature token. "
            "Sacrifice it at the beginning of the next end step."
        ),
    },

    # Exploit
    "exploit": {
        "event": "enters_battlefield",
        "condition": "When this creature enters the battlefield",
        "effect_template": (
            "you may sacrifice a creature. When you do, {exploit_effect}"
        ),
    },

    # Mentor
    "mentor": {
        "event": "attacks",
        "condition": "Whenever this creature attacks",
        "effect_template": (
            "put a +1/+1 counter on target attacking creature with lesser power."
        ),
    },

    # Battalion
    "battalion": {
        "event": "attacks",
        "condition": "Whenever this and at least two other creatures attack",
        "effect_template": "{battalion_effect}",
    },

    # Raid
    "raid": {
        "event": "enters_battlefield",
        "condition": "When this creature enters the battlefield, if you attacked this turn",
        "effect_template": "{raid_effect}",
    },

    # Heroic
    "heroic": {
        "event": "spell_cast_targeting_this",
        "condition": "Whenever you cast a spell that targets this creature",
        "effect_template": "{heroic_effect}",
    },
}

def derive_keyword_abilities(axis1_card: Axis1Card, game_state: "GameState") -> List[str]:
    text = (axis1_card.faces[0].oracle_text or "").lower()
    found: List[str] = []

    # 1. Evergreen keywords
    for kw in KEYWORD_ABILITIES:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            found.append(kw)

    # 2. Ward {X}
    if re.search(r"ward\s*\{", text):
        found.append("ward")

    # 3. Protection
    if "protection from" in text:
        found.append("protection")

    # 4. Annihilator
    if re.search(r"annihilator\s+\d+", text):
        found.append("annihilator")

    # 5. Delirium
    if re.search(r"\bdelirium\b", text):
        found.append("delirium")

    # 6. Convoke (if not already caught)
    if "convoke" in text:
        found.append("convoke")

    # IMPORTANT:
    # Do NOT include keyword-trigger abilities here.
    # They belong in the trigger parser, not the keyword parser.

    return list(dict.fromkeys(found))

