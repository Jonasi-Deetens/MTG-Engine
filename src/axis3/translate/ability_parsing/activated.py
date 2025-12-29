import re
from typing import List, Union

from axis1.schema import Axis1Card  # adjust/import Axis1Face if you have it
from axis2.schema import ActivatedAbility
from axis3.translate.ability_parsing.costs import parse_cost_string
from axis3.translate.ability_parsing.effects import parse_effect_string


# ---------------------------------------------------------------------------
# Helpers for multi-line ability grouping
# ---------------------------------------------------------------------------

# Lines that *start* a potential activated ability.
# We keep this broad; we filter more precisely later.
ABILITY_HEAD_START_PATTERN = re.compile(
    r"""^(
        (?:\{[^}]+\})+                              # {T}, {1}{G}, {R/P}, {G/U}, etc.
        |
        Tap\b
        |
        Untap\b
        |
        Sacrifice\b
        |
        Discard\b
        |
        Exile\b
        |
        Return\b
        |
        Pay\b
        |
        Lose\b
        |
        Reveal\b
        |
        Mill\b
        |
        Remove\b
    )""",
    re.IGNORECASE | re.VERBOSE,
)

# Bullet markers for modal/continued text
BULLET_PATTERN = re.compile(r"^\s*(?:•|-|—)\s+")


def _is_bullet_or_continuation(line: str) -> bool:
    """
    A line belongs to the previous ability if:
    - it is indented, or
    - it starts with a bullet marker (•, -, —)
    """
    if not line:
        return False
    if BULLET_PATTERN.match(line):
        return True
    # Any leading whitespace means continuation
    return line[0].isspace()


def _collect_ability_blocks(text: str) -> List[str]:
    """
    Group multi-line activated abilities based on:
    - a head line that looks like a cost/EFFECT line
    - subsequent indented or bullet lines belonging to it
    """
    blocks: List[List[str]] = []
    current: List[str] = []

    for raw in text.splitlines():
        # Normalize NBSP, keep raw indentation
        line = raw.replace("\u00A0", " ")
        stripped = line.strip()

        # Strip wrapping reminder parentheses
        if stripped.startswith("(") and stripped.endswith(")"):
            stripped = stripped[1:-1].strip()

        if not stripped:
            # Empty line: terminate current block if we have one
            if current:
                blocks.append(current)
                current = []
            continue

        if ABILITY_HEAD_START_PATTERN.match(stripped) and ":" in stripped:
            # New ability head
            if current:
                blocks.append(current)
            current = [stripped]
        elif current and _is_bullet_or_continuation(line):
            # Continuation of current ability (keep stripped to simplify parsing)
            current.append(stripped)
        else:
            # Standalone non-ability line: flush current block if any
            if current:
                blocks.append(current)
                current = []
            # Otherwise ignore; could be static text, flavor, etc.

    if current:
        blocks.append(current)

    # Join each block into a single logical string (head + continuation lines)
    return [" ".join(b).strip() for b in blocks]


# ---------------------------------------------------------------------------
# Cost/effect head parsing
# ---------------------------------------------------------------------------

# 1. Pure symbol costs: "{T}: Do X", "{2}{G}{G}: Do X"
SYMBOL_COST_HEAD_PATTERN = re.compile(
    r"""
    ^
    (?P<cost>(?:\{[^}]+\})+)
    \s*:\s*
    (?P<effect>.+)
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

# 2. Symbol + additional text costs: "{2}{G}, Sacrifice a creature: Do X"
SYMBOL_PLUS_TEXT_COST_HEAD_PATTERN = re.compile(
    r"""
    ^
    (?P<cost>(?:\{[^}]+\})+\s*,\s*[^:]+?)
    \s*:\s*
    (?P<effect>.+)
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

# 3. Tap/Untap/other word-based costs including numbers & punctuation
#    Examples:
#    "Tap two untapped tokens you control: Add one mana of any color."
#    "Sacrifice a creature: Draw a card."
#    "Pay 3 life: Draw a card."
WORD_COST_HEAD_PATTERN = re.compile(
    r"""
    ^
    (?P<cost>
        (?:
            Tap
            |
            Untap
            |
            Sacrifice
            |
            Discard
            |
            Exile
            |
            Return
            |
            Pay
            |
            Lose
            |
            Reveal
            |
            Mill
            |
            Remove
        )
        [^:]*?             # everything up to the colon, lazily
    )
    \s*:\s*
    (?P<effect>.+)
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

# 4. Very general fallback for any word-based cost phrase ending in colon.
#    Includes digits, commas, apostrophes, hyphens.
GENERIC_COST_HEAD_PATTERN = re.compile(
    r"""
    ^
    (?P<cost>
        [A-Za-z0-9][A-Za-z0-9 ,'"\-]*
    )
    \s*:\s*
    (?P<effect>.+)
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _split_cost_and_effect(head: str) -> Union[None, tuple[str, str]]:
    """
    Try to split a 'COST: EFFECT' head string into (cost_str, effect_str)
    using a series of increasingly generic patterns.
    """
    for pattern in (
        SYMBOL_PLUS_TEXT_COST_HEAD_PATTERN,
        SYMBOL_COST_HEAD_PATTERN,
        WORD_COST_HEAD_PATTERN,
        GENERIC_COST_HEAD_PATTERN,
    ):
        m = pattern.match(head)
        if m:
            cost = m.group("cost").strip()
            effect = m.group("effect").strip()
            return cost, effect
    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def _get_oracle_text(card_or_face: Union[Axis1Card, object]) -> str:
    """
    Accept either an Axis1Card (with .faces[0].oracle_text) or a face-like
    object with .oracle_text directly.
    """
    if isinstance(card_or_face, Axis1Card):
        face = card_or_face.faces[0]
        return face.oracle_text or ""
    # Fallback for face-like objects (Axis1Face or similar)
    text = getattr(card_or_face, "oracle_text", "") or ""
    return text


def derive_activated_abilities(card_or_face: Union[Axis1Card, object]) -> List[ActivatedAbility]:
    """
    Derive activated abilities from Oracle text, supporting:
    - Multi-line activated abilities (indentation / bullets)
    - Symbol costs ({T}, {1}{G}, hybrid, Phyrexian, etc.)
    - Word-based costs (Tap, Sacrifice, Discard, Exile, Pay life, Remove counters, etc.)
    - Multi-part costs ({2}{G}, Sacrifice a creature)
    - Modal abilities with bullets (•, -, —)

    Deep semantics of costs and effects are delegated to:
    - axis3.translate.ability_parsing.costs.parse_cost_string
    - axis3.translate.ability_parsing.effects.parse_effect_string
    """
    text = _get_oracle_text(card_or_face)
    if not text:
        return []

    abilities: List[ActivatedAbility] = []

    # 1. Group multi-line blocks that look like activated abilities
    blocks = _collect_ability_blocks(text)

    for block in blocks:
        # For parsing head, we only care about cost/effect head.
        # Continuation text (modes, conditions) is included in the effect
        # by virtue of us joining the block into a single string earlier.
        head = block

        split = _split_cost_and_effect(head)
        if not split:
            # Couldn't recognize COST: EFFECT shape; skip this block.
            continue

        cost_str, effect_str = split

        # 2. Delegate to Axis3 cost/effect parsers
        try:
            cost_objs = parse_cost_string(cost_str)
        except Exception:
            # If cost parsing fails, treat as no-cost unparsed ability
            cost_objs = []

        try:
            # Remove reminder text in parentheses
            effect_str = re.sub(r"\([^)]*\)", "", effect_str).strip()
            effect_objs, is_mana = parse_effect_string(effect_str)
        except Exception:
            # If effect parsing fails, treat as no-effect non-mana ability
            effect_objs = []
            is_mana = False

        # 3. Build ActivatedAbility for Axis2/Axis3 bridge
        #    (restrictions can be enriched later if you add parsing)
        abilities.append(
            ActivatedAbility(
                cost=cost_objs,
                effect=effect_objs,
                is_mana_ability=is_mana,
                restrictions=[],
            )
        )

    return abilities
