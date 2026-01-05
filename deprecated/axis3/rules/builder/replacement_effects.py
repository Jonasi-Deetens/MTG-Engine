import re
from typing import List, Dict, Any

from axis1.schema import Axis1Card
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from axis3.state.game_state import GameState


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _oracle_text(axis1_card: Axis1Card) -> str:
    face = axis1_card.faces[0]
    return (face.oracle_text or "").strip().lower()


def _regex(text: str, pattern: str):
    return re.search(pattern, text, re.IGNORECASE)


# ------------------------------------------------------------
# Patterns for replacement / prevention text
# ------------------------------------------------------------

# Generic "If X would Y, do Z instead"
GENERIC_REPLACEMENT_PATTERN = re.compile(
    r"if (?P<subject>.+?) would (?P<event>enter the battlefield|die|be dealt damage|be put into a graveyard from anywhere|deal damage|draw a card|mill cards?), (?P<replacement>.+?) instead\.",
    re.IGNORECASE,
)

# Dies → exile instead
DIES_EXILE_PATTERN = re.compile(
    r"if (?P<object>.+?) would die, exile (it|that creature) instead",
    re.IGNORECASE,
)

# ETB tapped (replacement flavor)
ETB_TAPPED_PATTERN = re.compile(
    r"(?P<object>this|it|[a-zA-Z0-9 ,'\-]+?) "
    r"enter(?:s)?(?: the battlefield)? tapped",
    re.IGNORECASE,
)

# Draw replacement
DRAW_REPLACEMENT_PATTERN = re.compile(
    r"if (?P<subject>you|a player) would draw (?:a card|one or more cards), (?P<replacement>.+?) instead",
    re.IGNORECASE,
)

# Damage prevention / replacement
DAMAGE_PREVENT_PATTERN = re.compile(
    r"prevent all (?P<combat>combat )?damage that would be dealt to (?P<target>you|creatures you control|any target|[a-z ]+)",
    re.IGNORECASE,
)

# “Instead” of damage (e.g., redirect, gain life)
DAMAGE_INSTEAD_PATTERN = re.compile(
    r"if (?P<source>.+?) would deal damage, (?P<replacement>.+?) instead",
    re.IGNORECASE,
)

VIGOR_PATTERN = re.compile(
    r"if damage would be dealt to (?P<target>another creature you control|a creature you control|[a-z ]+),\s*prevent that damage",
    re.IGNORECASE
)



# ------------------------------------------------------------
# Oracle-text-based replacement parsing
# ------------------------------------------------------------

def _parse_oracle_replacements(axis1_card: Axis1Card) -> List[Dict[str, Any]]:
    text = _oracle_text(axis1_card)
    effects: List[Dict[str, Any]] = []

    # Generic "If X would Y, do Z instead"
    for m in GENERIC_REPLACEMENT_PATTERN.finditer(text):
        effects.append(
            {
                "type": "generic_replacement",
                "subject": m.group("subject").strip(),
                "event": m.group("event").strip(),
                "replacement": m.group("replacement").strip(),
            }
        )

    # Dies → exile instead
    for m in DIES_EXILE_PATTERN.finditer(text):
        effects.append(
            {
                "type": "dies_exile_instead",
                "subject": m.group("object").strip(),
                "event": "die",
                "replacement": "exile",
            }
        )

    # ETB tapped
    for m in ETB_TAPPED_PATTERN.finditer(text):
        effects.append(
            {
                "type": "enter_tapped",
                "subject": m.group("object").strip(),
                "event": "enter_battlefield",
                "replacement": "enter_tapped",
            }
        )

    # Draw replacement
    for m in DRAW_REPLACEMENT_PATTERN.finditer(text):
        effects.append(
            {
                "type": "draw_replacement",
                "subject": m.group("subject").strip(),
                "event": "draw",
                "replacement": m.group("replacement").strip(),
            }
        )

    # Damage prevention
    for m in DAMAGE_PREVENT_PATTERN.finditer(text):
        effects.append(
            {
                "type": "prevent_damage",
                "subject": m.group("target").strip(),
                "event": "damage",
                "combat_only": bool(m.group("combat")),
                "replacement": "prevent",
            }
        )

    # Damage replacement “instead”
    for m in DAMAGE_INSTEAD_PATTERN.finditer(text):
        effects.append(
            {
                "type": "damage_replacement",
                "subject": m.group("source").strip(),
                "event": "deal_damage",
                "replacement": m.group("replacement").strip(),
            }
        )

    # Vigor-style prevention: "If damage would be dealt to X, prevent that damage"
    for m in VIGOR_PATTERN.finditer(text):
        effects.append(
            {
                "type": "prevent_damage",
                "subject": m.group("target").strip(),
                "event": "damage",
                "replacement": "prevent_and_counter",
                "counter_type": "+1/+1",
                "per_damage": 1,
            }
        )


    return effects


# ------------------------------------------------------------
# Global / game-state replacement effects
# ------------------------------------------------------------

def _from_game_state(game_state: "GameState") -> List[Dict[str, Any]]:
    """
    Normalize whatever is in game_state.replacement_effects into a dict list.
    """
    effects: List[Dict[str, Any]] = []

    for effect in getattr(game_state, "replacement_effects", []):
        if isinstance(effect, str):
            effects.append({"type": effect})
        elif isinstance(effect, dict):
            effects.append(effect)

    return effects


# ------------------------------------------------------------
# Main replacement derivation
# ------------------------------------------------------------

def derive_replacement_effects(axis1_card: Axis1Card, game_state: "GameState") -> List[Dict[str, Any]]:
    """
    Extract replacement and prevention effects from oracle text and game state.
    Returns a list of dicts; you can later wrap these in a ReplacementEffect dataclass.
    """

    effects: List[Dict[str, Any]] = []

    # 1. From oracle text
    effects.extend(_parse_oracle_replacements(axis1_card))

    # 2. From game state (global replacement/prevention effects)
    effects.extend(_from_game_state(game_state))

    # 3. Deduplicate
    unique: List[Dict[str, Any]] = []
    seen = set()
    for e in effects:
        key = (e.get("type"), e.get("subject"), e.get("event"), e.get("replacement"))
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique
