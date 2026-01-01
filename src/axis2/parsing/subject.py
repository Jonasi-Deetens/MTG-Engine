import re

from typing import Optional, Dict, List
from axis2.schema import Subject, ParseContext

TYPE_WORDS = ["creature", "enchantment", "artifact", "planeswalker", "land", "permanent", "spell"]
CARD_TYPE_WORDS = ["creature", "enchantment", "artifact", "planeswalker", "instant", "sorcery"]
PLURAL_TYPES = {
    "creatures": "creature",
    "enchantments": "enchantment",
    "artifacts": "artifact",
    "planeswalkers": "planeswalker",
    "lands": "land",
    "permanents": "permanent",
    "spells": "spell",
}

CONTROLLER_PATTERNS = [
    (r"\byou control\b",        "you"),
    (r"\byour control\b",       "you"),
    (r"\byour opponents? control\b", "opponent"),
    (r"\bopponents? control\b", "opponent"),
    (r"\ban opponent controls\b", "opponent"),
]

OPPONENT_PATTERNS = [
    r"\bopponent\b",
    r"\bopponents\b",
]

PLAYER_WORDS = ["player", "players"]
OPPONENT_WORDS = ["opponent", "opponents"]


def _detect_scope(t: str) -> str:
    """
    Decide the subject scope:
    - 'linked_exiled_card', 'that', 'it', 'them', 'each', 'target', 'self'
    """
    # linked exiled card handled separately in main function

    # explicit "each" / plural non-target subjects (creatures you control, etc.)
    if re.search(r"\beach\b", t):
        return "each"

    # "each player", "each opponent"
    if re.search(r"\beach (player|opponent)\b", t):
        return "each"

    # targeted things
    if "target" in t:
        return "target"

    # pronoun references
    if re.search(r"\bit\b", t) or re.search(r"\bthem\b", t) or re.search(r"\bthat (creature|player|permanent|spell)\b", t):
        return "that"

    # fallback: self
    return "self"


def _detect_controller(t: str) -> Optional[str]:
    """
    Detect controller context: 'you', 'opponent', or None.
    """
    for pattern, who in CONTROLLER_PATTERNS:
        if re.search(pattern, t):
            return who

    # "target opponent", "each opponent", etc.
    for pat in OPPONENT_PATTERNS:
        if re.search(pat, t):
            return "opponent"

    return None


def _detect_player_subject(t: str, scope: str, controller: Optional[str]):
    """
    Detect when the subject is a player / opponent rather than a permanent/card.
    Returns (is_player_subject: bool, types_override, filters_override)
    """
    if any(w in t for w in PLAYER_WORDS) or any(w in t for w in OPPONENT_WORDS):
        # 'target player', 'each opponent', 'target opponent'
        # Represent as types=None, but add a role filter for clarity
        filters: Dict[str, object] = {}
        if controller == "opponent":
            filters["role"] = "opponent"
        elif "player" in t:
            filters["role"] = "player"

        return True, None, filters

    return False, None, {}


def _detect_types(t: str) -> Optional[List[str]]:
    """
    Infer the type list: ['creature'], ['permanent'], etc.
    Handles plural and singular, and 'X card' forms.
    """
    # plural forms first
    for plural, singular in PLURAL_TYPES.items():
        if re.search(rf"\b{plural}\b", t):
            return [singular]

    # card forms: "creature card", "enchantment card", etc.
    if "card" in t:
        for type_word in CARD_TYPE_WORDS:
            if re.search(rf"\b{type_word}\s+card\b", t):
                return [type_word]

    # singular type words
    for type_word in TYPE_WORDS:
        if re.search(rf"\b{type_word}\b", t):
            return [type_word]

    return None


def _detect_basic_filters(t: str) -> Dict[str, object]:
    """
    Filters that don't depend on zones or numeric values:
    - another, nonland, legendary, token, subtype-ish 'god' if you want, etc.
    """
    filters: Dict[str, object] = {}

    if "another" in t:
        filters["not_self"] = "self"

    if "nonland" in t:
        filters["nonland"] = True

    # Simple legendary / nonlegendary hooks if you ever want them
    if "legendary" in t and "nonlegendary" not in t:
        filters["legendary"] = True
    if "nonlegendary" in t:
        filters["legendary"] = False

    # You can grow this later with specific subtype hooks if you want:
    # if "god" in t: filters["subtype"] = "God"

    return filters


def subject_from_text(raw: str, ctx: ParseContext, extra_filters: Optional[Dict[str, object]] = None) -> Subject:
    """
    Full working subject parser for Axis2.
    Handles:
      - target X / another target X
      - nonland permanent
      - creatures / enchantments / artifacts / lands / permanents (plural)
      - 'you control', 'an opponent controls', 'your opponents control'
      - 'the exiled card'
      - 'it', 'them', 'that creature', 'that player'
      - player vs permanent subjects

    extra_filters are merged on top of what we detect from text.
    """
    t = raw.lower().strip()
    filters: Dict[str, object] = {}

    if extra_filters:
        filters.update(extra_filters)

    card_name = ctx.card_name
    card_primary_type = ctx.primary_type
    print(f"Card name: {card_name}, Card primary type: {card_primary_type}")
    # 1. Linked exiled card (Oblivion Ring, Banishing Light, etc.)
    if "the exiled card" in t:
        return Subject(
            scope="linked_exiled_card",
            controller=None,
            types=None,
            filters={"source": "self"},
        )

    # 1a. Explicit "this X" references
    if "this creature" in t:
        return Subject(scope="self", controller=None, types=["creature"], filters={})

    if "this permanent" in t:
        return Subject(scope="self", controller=None, types=["permanent"], filters={})

    if "this enchantment" in t:
        return Subject(scope="self", controller=None, types=["enchantment"], filters={})

    if "this artifact" in t:
        return Subject(scope="self", controller=None, types=["artifact"], filters={})

    if "this spell" in t:
        return Subject(scope="self", controller=None, types=["spell"], filters={})

    # 1b. Self-reference by card name
    normalized_name = card_name.lower().split(",")[0].strip()
    if normalized_name in t:
        return Subject(
            scope="self",
            controller=None,
            types=[card_primary_type],  # e.g. "creature"
            filters={}
        )

    # 2. Determine scope
    scope = _detect_scope(t)

    # 3. Controller
    controller = _detect_controller(t)
    if controller:
        filters["controller"] = controller

    # 4. Player vs permanent/card subject
    is_player_subject, player_types, player_filters = _detect_player_subject(t, scope, controller)
    if is_player_subject:
        filters.update(player_filters)
        return Subject(
            scope=scope,
            controller=controller,
            types=player_types,  # usually None
            filters=filters,
        )

    # 5. Basic filters (another, nonland, legendary, etc.)
    basic_filters = _detect_basic_filters(t)
    filters.update(basic_filters)

    # 6. Types (creature, enchantment, permanent, etc.)
    types = _detect_types(t)

    # 7. Fallback: if we have no types and no obvious structure, keep raw for debugging
    if types is None and not filters and scope == "self":
        filters["raw"] = raw

    return Subject(
        scope=scope,
        controller=controller,
        types=types,
        filters=filters,
    )


def parse_subject(text: str) -> Subject | None:
    t = text.lower()

    # ----------------------------------------
    # 1. Scope detection
    # ----------------------------------------
    print(f"Parsing subject: {t}")
    # Plural subjects imply "each"
    if re.search(r"\bcreatures\b", t):
        scope = "each"
    elif "target" in t:
        scope = "target"
    elif "each" in t:
        scope = "each"
    elif "any number of" in t:
        scope = "any_number"
    elif "up to" in t:
        scope = "up_to_n"
    else:
        scope = None


    # ----------------------------------------
    # 2. Controller detection
    # ----------------------------------------
    controller = None
    if "you control" in t:
        controller = "you"
    elif "your opponents control" in t:
        controller = "opponents"
    elif "opponent controls" in t:
        controller = "opponent"
    elif "each opponent" in t:
        controller = "opponent"
    elif "opponent" in t:
        controller = "opponent"

    # ----------------------------------------
    # 3. Type detection
    # ----------------------------------------
    types = []
    for typ in ["creature", "player", "planeswalker", "artifact", "enchantment", "land", "permanent"]:
        if typ in t:
            types.append(typ)

    if not types:
        types = None

    # ----------------------------------------
    # 4. Filters (keywords, power, etc.)
    # ----------------------------------------
    filters = {}

    if "with flying" in t:
        filters["keyword"] = "flying"

    if "creature type of your choice" in t:
        filters["chosen_type"] = True



    # TODO: add more filters later

    if not filters:
        filters = None

    # ----------------------------------------
    # 5. Max targets (for "up to N targets")
    # ----------------------------------------
    max_targets = None
    m = re.search(r"up to (\d+)", t)
    if m:
        max_targets = int(m.group(1))

    # ----------------------------------------
    # 6. Return structured subject
    # ----------------------------------------
    if scope or controller or types or filters:
        return Subject(
            scope=scope,
            controller=controller,
            types=types,
            filters=filters,
            max_targets=max_targets
        )

    return None
