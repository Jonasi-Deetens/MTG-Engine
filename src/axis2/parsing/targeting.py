# axis2/parsing/targeting.py

import re
from axis2.schema import TargetingRules

"""
Generalized targeting parser.

Goals:
- Extract target type(s) (creature, player, planeswalker, permanent, spell, etc.).
- Extract restrictions (nonland, not_self, controller-based, etc.).
- Handle "another target nonland permanent" and similar patterns.
- Be easily extensible without card-specific hacks.
"""

# ------------------------------
# Regexes and keyword groups
# ------------------------------

# Basic targeting anchor: we only care about text that actually targets.
TARGET_WORD_RE = re.compile(r"\btarget\b", re.IGNORECASE)

# Some useful groups for detection
TYPE_KEYWORDS = {
    "creature": "creature",
    "player": "player",
    "planeswalker": "planeswalker",
    "permanent": "permanent",
    "artifact": "artifact",
    "enchantment": "enchantment",
    "land": "land",
    "nonland permanent": "permanent",  # type is still permanent; "nonland" is a restriction
    "spell": "spell",
    "noncreature spell": "spell",      # type is still spell; "noncreature" is a restriction
}

# Ordered patterns so we match more specific phrases first.
TYPE_PATTERNS = [
    # Compound types
    (re.compile(r"\btarget player or planeswalker\b", re.IGNORECASE),
     ["player", "planeswalker"], []),

    (re.compile(r"\btarget creature or planeswalker\b", re.IGNORECASE),
     ["creature", "planeswalker"], []),

    # Any target (creature, player, planeswalker)
    (re.compile(r"\bany target\b", re.IGNORECASE),
     ["any_target"], []),

    # Nonland permanent (Oblivion Ring, Detention Sphere, etc.)
    (re.compile(r"\btarget nonland permanent\b", re.IGNORECASE),
     ["permanent"], ["nonland"]),

    # Generic permanent
    (re.compile(r"\btarget permanent\b", re.IGNORECASE),
     ["permanent"], []),

    # Noncreature spell
    (re.compile(r"\btarget noncreature spell\b", re.IGNORECASE),
     ["spell"], ["noncreature"]),

    # Spell
    (re.compile(r"\btarget spell\b", re.IGNORECASE),
     ["spell"], []),

    # Artifact
    (re.compile(r"\btarget artifact\b", re.IGNORECASE),
     ["artifact"], []),

    # Enchantment
    (re.compile(r"\btarget enchantment\b", re.IGNORECASE),
     ["enchantment"], []),

    # Land
    (re.compile(r"\btarget land\b", re.IGNORECASE),
     ["land"], []),

    # Creature you control / an opponent controls
    (re.compile(r"\btarget creature you control\b", re.IGNORECASE),
     ["creature"], ["you_control"]),

    (re.compile(r"\btarget creature an opponent controls\b", re.IGNORECASE),
     ["creature"], ["opponent_controls"]),

    (re.compile(r"\btarget creature you don['’]t control\b", re.IGNORECASE),
     ["creature"], ["not_controller"]),

    # Generic creature
    (re.compile(r"\btarget creature\b", re.IGNORECASE),
     ["creature"], []),

    # Opponent
    (re.compile(r"\btarget opponent\b", re.IGNORECASE),
     ["player"], ["opponent"]),

    # Player
    (re.compile(r"\btarget player\b", re.IGNORECASE),
     ["player"], []),

    # Planeswalker
    (re.compile(r"\btarget planeswalker\b", re.IGNORECASE),
     ["planeswalker"], []),
]

# Restrictions that are not tied to a specific type pattern
ADDITIONAL_RESTRICTIONS = [
    # Another / not self
    (re.compile(r"\banother target\b", re.IGNORECASE), "not_self"),
    (re.compile(r"\banother\b", re.IGNORECASE), "not_self"),

    # Control-based (beyond the specific "creature you control" handled above)
    (re.compile(r"\byou control\b", re.IGNORECASE), "you_control"),
    (re.compile(r"\byou don['’]t control\b", re.IGNORECASE), "not_controller"),

    # Opponent-based
    (re.compile(r"\ban opponent controls\b", re.IGNORECASE), "opponent_controls"),
    (re.compile(r"\bopponent\b", re.IGNORECASE), "opponent"),

    # Nonland generic (in case it appears outside "nonland permanent")
    (re.compile(r"\bnonland\b", re.IGNORECASE), "nonland"),

    # Noncreature generic (outside "noncreature spell")
    (re.compile(r"\bnoncreature\b", re.IGNORECASE), "noncreature"),

    # "Up to" can affect min=0 vs min=1, but we keep that in a separate pass for now.
]


def parse_targeting(text: str) -> TargetingRules | None:
    """
    Extract generalized targeting rules from an effect or ability text.

    Handles:
      - target creature
      - target player
      - target planeswalker
      - target player or planeswalker
      - target creature or planeswalker
      - any target
      - target nonland permanent
      - target permanent
      - target spell / noncreature spell
      - target artifact/enchantment/land
      - target creature you control / an opponent controls / you don't control
      - 'another' as a not_self restriction
    """
    if not text:
        return None

    t = text.lower()
    if not TARGET_WORD_RE.search(t):
        return None

    # Default: single required target
    rules = TargetingRules(required=True, min=1, max=1)
    rules.legal_targets = []
    # Assume schema gives rules.restrictions a default list; if not, initialize:
    if rules.restrictions is None:
        rules.restrictions = []

    # -----------------------------------------
    # 1. Handle "up to N", "any number of", etc.
    # -----------------------------------------
    # Up to one target ...
    if re.search(r"\bup to one target\b", t):
        rules.min = 0
        rules.max = 1

    # Up to two targets, up to three targets, etc.
    m_up_to_n = re.search(r"\bup to (\d+) target", t)
    if m_up_to_n:
        n = int(m_up_to_n.group(1))
        rules.min = 0
        rules.max = n

    # Any number of target ...
    if re.search(r"\bany number of target\b", t):
        rules.min = 0
        rules.max = 999  # effectively unbounded; Axis3 can interpret this

    # Exactly N targets (rare, but possible)
    m_exact_n = re.search(r"\b(\d+) target (creature|player|permanent|opponent|planeswalker)", t)
    if m_exact_n:
        n = int(m_exact_n.group(1))
        rules.min = n
        rules.max = n

    # -----------------------------------------
    # 2. Detect primary target type(s)
    # -----------------------------------------
    for pattern, types, restrictions in TYPE_PATTERNS:
        if pattern.search(t):
            rules.legal_targets = types
            rules.restrictions.extend(restrictions)
            break

    # Fallback if we still haven't found a specific type
    if not rules.legal_targets:
        # "any target" was already handled; if we reach here,
        # we assume "any" permanent/object/player/spell etc.
        rules.legal_targets = ["any"]

    # -----------------------------------------
    # 3. Add generic restrictions not tied to specific patterns
    # -----------------------------------------
    for pattern, restriction in ADDITIONAL_RESTRICTIONS:
        if pattern.search(t) and restriction not in rules.restrictions:
            rules.restrictions.append(restriction)

    return rules
