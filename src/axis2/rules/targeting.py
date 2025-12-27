import re
from typing import List, Optional, Tuple

from axis1.schema import Axis1Card
from axis2.schema import TargetingRules, TargetingRestriction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from axis2.builder import GameState


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _oracle_text(axis1_card: Axis1Card) -> str:
    face = axis1_card.faces[0]
    return (face.oracle_text or "").strip()


def _lower(text: str) -> str:
    return text.lower()


def _regex(text: str, pattern: str):
    return re.search(pattern, text, re.IGNORECASE)


# ------------------------------------------------------------
# Target Count Parsing
# ------------------------------------------------------------

def _parse_target_counts(text: str) -> Tuple[int, int, bool]:
    """
    Returns (min, max, required).
    Handles:
      - "target" → 1
      - "two target creatures" → 2
      - "each of up to two target creatures" → 0–2
      - "each of up to X target" → 0–X
      - "up to one target" → 0–1
      - "up to two target" → 0–2
      - "any number of targets" → 0–∞
      - "any number of target instant and/or sorcery spells" → 0–∞
    """

    t = text.lower()

    # Any number of targets
    if "any number of target" in t or "any number of targets" in t:
        return 0, 99, False

    # Each of up to N target ...
    m = re.search(r"each of up to (\w+) target", t)
    if m:
        word = m.group(1)
        mapping = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
        }
        max_targets = mapping.get(word, 1)
        return 0, max_targets, False

    # Up to N target ...
    m = re.search(r"up to (\w+) target", t)
    if m:
        word = m.group(1)
        mapping = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
        }
        max_targets = mapping.get(word, 1)
        return 0, max_targets, False

    # N target creatures / permanents / etc.
    m = re.search(r"(\w+)\s+target\s+(creature|player|permanent|planeswalker|spell|land|battle)", t)
    if m:
        word = m.group(1)
        mapping = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
        }
        if word in mapping:
            return mapping[word], mapping[word], True

    # Default: if "target" appears at all, assume exactly one
    if "target " in t:
        return 1, 1, True

    return 0, 0, False


# ------------------------------------------------------------
# Legal Target Type Parsing
# ------------------------------------------------------------

# Base categories – these are *permanent* or generic classes.
BASE_LEGAL_TYPES = [
    "creature", "player", "opponent", "artifact", "enchantment",
    "planeswalker", "land", "permanent", "battle", "token",
    "nonland_permanent", "noncreature_permanent", "noncreature_spell",
    "nonartifact_creature", "creature_spell", "instant_spell",
    "sorcery_spell", "spell", "creature_card", "instant_card",
    "sorcery_card", "card", "card_in_graveyard", "card_in_exile",
]


def _parse_spell_target_types(t: str, legal: List[str]) -> None:
    """
    Add spell-target classes like instant_spell, sorcery_spell, spell,
    creature_spell, noncreature_spell, etc.
    """

    # Generic "target spell"
    if "target spell" in t and "spell" not in legal:
        legal.append("spell")

    # "target instant spell" / "target sorcery spell"
    if "target instant spell" in t and "instant_spell" not in legal:
        legal.append("instant_spell")
    if "target sorcery spell" in t and "sorcery_spell" not in legal:
        legal.append("sorcery_spell")

    # "target instant or sorcery spell" / "target instant and/or sorcery spell"
    if "target instant or sorcery spell" in t or "target instant and/or sorcery spell" in t:
        if "instant_spell" not in legal:
            legal.append("instant_spell")
        if "sorcery_spell" not in legal:
            legal.append("sorcery_spell")

    # "target creature spell"
    if "target creature spell" in t and "creature_spell" not in legal:
        legal.append("creature_spell")

    # "target noncreature spell"
    if "target noncreature spell" in t and "noncreature_spell" not in legal:
        legal.append("noncreature_spell")


def _parse_graveyard_exile_targets(t: str, legal: List[str]) -> None:
    """
    Handle 'target creature card in your graveyard', 'target card in a graveyard', etc.
    This is coarse – Axis3 will refine by zone and type.
    """

    # Generic card in graveyard
    if "target card in your graveyard" in t or "target card in a graveyard" in t:
        if "card_in_graveyard" not in legal:
            legal.append("card_in_graveyard")

    # Creature card in graveyard
    if "target creature card in your graveyard" in t or "target creature card in a graveyard" in t:
        if "creature_card" not in legal:
            legal.append("creature_card")

    # Instant / sorcery card in graveyard
    if "target instant or sorcery card in your graveyard" in t:
        if "instant_card" not in legal:
            legal.append("instant_card")
        if "sorcery_card" not in legal:
            legal.append("sorcery_card")

    if "target instant card in your graveyard" in t and "instant_card" not in legal:
        legal.append("instant_card")
    if "target sorcery card in your graveyard" in t and "sorcery_card" not in legal:
        legal.append("sorcery_card")

    # Card in exile
    if "target card in exile" in t and "card_in_exile" not in legal:
        legal.append("card_in_exile")


def _parse_multi_type_phrases(t: str, legal: List[str]) -> None:
    """
    Handle phrases like:
      - 'target creature or planeswalker'
      - 'target artifact or enchantment'
      - 'target creature or battle'
      - 'target artifact, creature, or enchantment'
    """

    combos = [
        ("target creature or player", ["creature", "player"]),
        ("target creature or planeswalker", ["creature", "planeswalker"]),
        ("target player or planeswalker", ["player", "planeswalker"]),
        ("target creature or battle", ["creature", "battle"]),
        ("target artifact or enchantment", ["artifact", "enchantment"]),
        ("target artifact or creature", ["artifact", "creature"]),
        ("target creature or enchantment", ["creature", "enchantment"]),
        ("target artifact, creature, or enchantment", ["artifact", "creature", "enchantment"]),
        ("target creature, planeswalker, or battle", ["creature", "planeswalker", "battle"]),
    ]

    for phrase, types in combos:
        if phrase in t:
            for typ in types:
                if typ not in legal:
                    legal.append(typ)


def _parse_non_x_targets(t: str, legal: List[str]) -> None:
    """
    Handle nonland / nonartifact / noncreature constraints that are expressed
    as 'nonland permanent', 'noncreature permanent', 'nonartifact creature', etc.
    """

    if "target nonland permanent" in t and "nonland_permanent" not in legal:
        legal.append("nonland_permanent")

    if "target noncreature permanent" in t and "noncreature_permanent" not in legal:
        legal.append("noncreature_permanent")

    if "target nonartifact creature" in t and "nonartifact_creature" not in legal:
        legal.append("nonartifact_creature")

    # Sometimes appears as "target noncreature spell" – handled in spell parser.
    # We also handle generic "target permanent"
    if "target permanent" in t and "permanent" not in legal:
        legal.append("permanent")


def _parse_simple_permanent_targets(t: str, legal: List[str]) -> None:
    """
    Handle simple permanent types and tokens.
    """

    base_types = [
        "creature", "player", "opponent", "artifact", "enchantment",
        "planeswalker", "land", "battle", "token",
    ]

    for typ in base_types:
        if f"target {typ}" in t and typ not in legal:
            legal.append(typ)

    # Nontoken
    if "target nontoken creature" in t and "creature" not in legal:
        legal.append("creature")


def _parse_legal_targets(text: str) -> List[str]:
    """
    Extract legal target types from oracle text.
    Handles:
      - 'target creature'
      - 'target creature or player'
      - 'target artifact, creature, or enchantment'
      - 'target instant and/or sorcery spell'
      - 'target creature spell'
      - 'target noncreature spell'
      - various graveyard / exile card patterns
    """

    t = text.lower()
    legal: List[str] = []

    # 0. Color‑qualified targets: "target red spell", "target blue creature", etc.
    COLOR_WORDS = {"white", "blue", "black", "red", "green"}

    for m in re.finditer(r"target\s+([a-z]+)\s+([a-z]+)", t):
        color, type_ = m.group(1), m.group(2)

        # If the first word is a color, treat it as a color restriction
        if color in COLOR_WORDS:
            # Add the type as a legal target
            if type_ in BASE_LEGAL_TYPES and type_ not in legal:
                legal.append(type_)

            # Also record the color restriction (handled in _parse_restrictions)
            # We do NOT add restrictions here — only legal types.
        else:
            # If the first word is NOT a color, treat it as a type
            if color in BASE_LEGAL_TYPES and color not in legal:
                legal.append(color)


    # 1. Multi-type combos (permanent / player / battle)
    _parse_multi_type_phrases(t, legal)

    # 2. Non-X permanents
    _parse_non_x_targets(t, legal)

    # 3. Spell targets (spells on the stack)
    _parse_spell_target_types(t, legal)

    # 4. Graveyard / exile
    _parse_graveyard_exile_targets(t, legal)

    # 5. Fallback: parse up to punctuation from a "target ..." segment
    #    Example: "target artifact, creature, or enchantment"
    m = re.search(r"target ([^\.]+?)(?:\.|$)", t)
    if m:
        segment = m.group(1)
        parts = re.split(r",|or|and", segment)
        for part in parts:
            p = part.strip()
            if p.startswith("target "):
                p = p[len("target "):].strip()
            # normalize plural
            if p.endswith("s"):
                p = p[:-1]
            # try to match against known types
            if p in BASE_LEGAL_TYPES and p not in legal:
                legal.append(p)

    # 6. Simple fallbacks – 'target creature', 'target player', etc.
    _parse_simple_permanent_targets(t, legal)

    return legal


# ------------------------------------------------------------
# Target Restrictions
# ------------------------------------------------------------

def _parse_restrictions(text: str) -> List[TargetingRestriction]:
    """
    Handles:
      - 'creature you control'
      - 'creature an opponent controls'
      - 'creature with flying'
      - 'creature without flying'
      - 'spell you control' / 'spell you don't control'
      - 'permanent you own but don't control'
      - 'attacking creature', 'blocking creature'
      - 'with power 4 or greater'
      - 'with mana value 3 or less'
      - 'legendary creature'
      - 'nonlegendary creature'
    """

    t = text.lower()
    restrictions: List[TargetingRestriction] = []
    conditions = []

    # Color-qualified targets: "target red spell", "target blue creature", etc.
    COLOR_WORDS = {"white", "blue", "black", "red", "green"}

    for m in re.finditer(r"target\s+([a-z]+)\s+([a-z]+)", t):
        color, type_ = m.group(1), m.group(2)
        if color in COLOR_WORDS:
            restrictions.append(
                TargetingRestriction(
                    type="color",
                    conditions=[{"color": color}],
                    logic=None,
                    optional=False,
                )
            )

    # Control-based restrictions (permanents / spells)
    if "you control" in t:
        conditions.append({"type": "control", "controller": "you"})
    if "an opponent controls" in t:
        conditions.append({"type": "control", "controller": "opponent"})
    if "you don't control" in t or "you do not control" in t:
        conditions.append({"type": "control", "controller": "not_you"})

    # Ownership vs control (e.g. 'permanent you own but don't control')
    if "you own but don't control" in t or "you own but do not control" in t:
        conditions.append({"type": "ownership", "owner": "you", "controller": "not_you"})

    # Keyword-based restrictions
    if "with flying" in t:
        conditions.append({"type": "keyword", "keyword": "flying"})
    if "without flying" in t:
        conditions.append({"type": "keyword_not", "keyword": "flying"})

    # Combat state
    if "attacking creature" in t:
        conditions.append({"type": "combat_state", "state": "attacking"})
    if "blocking creature" in t:
        conditions.append({"type": "combat_state", "state": "blocking"})

    # Power-based
    m = re.search(r"power (\d+) or greater", t)
    if m:
        conditions.append({"type": "power", "op": ">=", "value": int(m.group(1))})
    m = re.search(r"power (\d+) or less", t)
    if m:
        conditions.append({"type": "power", "op": "<=", "value": int(m.group(1))})

    # Mana value-based
    m = re.search(r"mana value (\d+) or less", t)
    if m:
        conditions.append({"type": "mana_value", "op": "<=", "value": int(m.group(1))})
    m = re.search(r"mana value (\d+) or greater", t)
    if m:
        conditions.append({"type": "mana_value", "op": ">=", "value": int(m.group(1))})

    # Legendary / nonlegendary
    if "legendary creature" in t:
        conditions.append({"type": "supertype", "supertype": "Legendary"})
    if "nonlegendary creature" in t:
        conditions.append({"type": "supertype_not", "supertype": "Legendary"})

    if conditions:
        restrictions.append(
            TargetingRestriction(
                type="compound",
                conditions=conditions,
                logic="AND",
                optional=False,
            )
        )

    return restrictions


# ------------------------------------------------------------
# Replacement Effects (ward, hexproof, protection)
# ------------------------------------------------------------

def _replacement_effects_from_game_state(axis1_card: Axis1Card, game_state: "GameState") -> List[str]:
    effects: List[str] = []
    for effect in game_state.replacement_effects:
        if isinstance(effect, str):
            effects.append(effect)
        else:
            kind = effect.get("type")
            if kind:
                effects.append(kind)
    return effects


# ------------------------------------------------------------
# Main Targeting Derivation
# ---------vvvvvvv---------------------------------------------------

def derive_targeting_from_spell_text(spell_text: str, game_state: "GameState") -> TargetingRules:
    """
    Derives cast-time targeting ONLY from the spell's own rules text.
    This prevents triggered-ability targeting from leaking into cast-time targeting.
    """
    if not spell_text:
        return TargetingRules(required=False, min=0, max=0, legal_targets=[])

    # Pattern: "Choose target X"
    m = re.search(r"choose\s+target\s+([a-zA-Z ]+)", spell_text, re.IGNORECASE)
    if m:
        target_type = m.group(1).strip().lower()

        # Normalize common target types
        if target_type == "creature":
            return TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["creature"],
                restrictions=[],
                replacement_effects=[]
            )

    # Pattern: "any target"
    m = re.search(r"\bany\s+target\b", spell_text, re.IGNORECASE)
    if m:
        return TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["any"],  # Axis3 expands this to creature/player/planeswalker/battle
            restrictions=[],
            replacement_effects=[]
        )


    # You can expand this table later

    # ------------------------------------------------------------
    # 1. AURA TARGETING: "Enchant X" always defines cast-time targets
    # ------------------------------------------------------------
    m = re.search(r"^Enchant\s+(.+)$", spell_text, re.IGNORECASE | re.MULTILINE)
    if m:
        target = m.group(1).strip().lower()

        # Normalize common Aura targets
        if target == "creature":
            return TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["creature"],
                restrictions=[],
                replacement_effects=[]
            )

        if target == "player":
            return TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["player"],
                restrictions=[],
                replacement_effects=[]
            )

        if target == "artifact":
            return TargetingRules(
                required=True,
                min=1,
                max=1,
                legal_targets=["artifact"],
                restrictions=[],
                replacement_effects=[]
            )

        # You can expand this table later for:
        # - Enchant land
        # - Enchant permanent
        # - Enchant creature you control
        # - Enchant planeswalker
        # - Enchant Equipment
        # - Enchant Giant
        # - Enchant Vehicle
        # etc.

    # ------------------------------------------------------------
    # 2. Fallback: normal targeting rules
    # ------------------------------------------------------------
    return derive_targeting_from_text(spell_text, game_state)


def derive_targeting_from_text(text: str, game_state) -> TargetingRules:
    t = text.lower()

    if "target" not in t:
        return TargetingRules(required=False, min=0, max=0, legal_targets=[], restrictions=[], replacement_effects=[])

    min_t, max_t, required = _parse_target_counts(text)
    legal = _parse_legal_targets(text)
    restrictions = _parse_restrictions(text)
    replacement_effects = []  # abilities rarely have ward/protection interactions

    return TargetingRules(
        required=required,
        min=min_t,
        max=max_t,
        legal_targets=legal,
        restrictions=restrictions,
        replacement_effects=replacement_effects,
    )


def derive_targeting(axis1_card: Axis1Card, game_state: "GameState") -> TargetingRules:
    """
    Full targeting parser for Axis2.
    """

    full_text = _oracle_text(axis1_card)
    # Only the first paragraph is spell text
    spell_text = full_text.split("\n")[0].strip().lower()

    # No targeting
    if "target" not in spell_text:
        return TargetingRules(
            required=False,
            min=0,
            max=0,
            legal_targets=[],
            restrictions=[],
            replacement_effects=[],
        )

    # Parse components
    min_t, max_t, required = _parse_target_counts(spell_text)
    legal = _parse_legal_targets(spell_text)
    restrictions = _parse_restrictions(spell_text)
    replacement_effects = _replacement_effects_from_game_state(axis1_card, game_state)

    return TargetingRules(
        required=required,
        min=min_t,
        max=max_t,
        legal_targets=legal,
        restrictions=restrictions,
        replacement_effects=replacement_effects,
    )
