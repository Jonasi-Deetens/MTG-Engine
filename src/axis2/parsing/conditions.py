# axis2/parsing/conditions.py

import re
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict


# ============================================================
# 1. Generic Condition Model
# ============================================================
from axis2.schema import Condition


# ============================================================
# 2. Shared helpers
# ============================================================

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10
}

def parse_number(raw: str) -> Optional[int]:
    raw = raw.lower()
    if raw.isdigit():
        return int(raw)
    return NUMBER_WORDS.get(raw)


# ============================================================
# 3. Condition Parsers
# ============================================================

# -----------------------------
# 3.1 Card Type Count (Delirium)
# -----------------------------
CARD_TYPE_COUNT_RE = re.compile(
    r"(?P<num>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"card types?\s+among\s+cards\s+in\s+your\s+graveyard",
    re.IGNORECASE
)

def parse_card_type_count_condition(text: str) -> Optional[Condition]:
    m = CARD_TYPE_COUNT_RE.search(text)
    if not m:
        return None

    n = parse_number(m.group("num"))
    return Condition(
        kind="card_type_count",
        zone="your_graveyard",
        min_value=n
    )


# -----------------------------
# 3.2 Card Count (Threshold, Metalcraft, Ascend)
# -----------------------------
CARD_COUNT_RE = re.compile(
    r"(?P<num>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?:or more|or fewer|or less|or greater|or at least|or at most)?\s*"
    r"(?P<subject>creatures|artifacts|permanents|lands|cards)\s+you\s+control",
    re.IGNORECASE
)

def parse_card_count_condition(text: str) -> Optional[Condition]:
    m = CARD_COUNT_RE.search(text)
    if not m:
        return None

    n = parse_number(m.group("num"))
    subject = m.group("subject").lower()

    return Condition(
        kind="card_count",
        subject=f"{subject} you control",
        min_value=n
    )


# -----------------------------
# 3.3 Threshold (cards in graveyard)
# -----------------------------
THRESHOLD_RE = re.compile(
    r"(?P<num>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"or more cards in your graveyard",
    re.IGNORECASE
)

def parse_threshold_condition(text: str) -> Optional[Condition]:
    m = THRESHOLD_RE.search(text)
    if not m:
        return None

    n = parse_number(m.group("num"))
    return Condition(
        kind="threshold",
        zone="your_graveyard",
        min_value=n
    )


# -----------------------------
# 3.4 Domain
# -----------------------------
def parse_domain_condition(text: str) -> Optional[Condition]:
    if "basic land types" in text.lower():
        return Condition(kind="domain")
    return None


# -----------------------------
# 3.5 Coven (different powers)
# -----------------------------
COVEN_RE = re.compile(
    r"(?P<num>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"creatures\s+you\s+control\s+with\s+different\s+powers",
    re.IGNORECASE
)

def parse_coven_condition(text: str) -> Optional[Condition]:
    m = COVEN_RE.search(text)
    if not m:
        return None

    n = parse_number(m.group("num"))
    return Condition(
        kind="power_diversity",
        subject="creatures you control",
        min_value=n
    )


# -----------------------------
# 3.6 Power Threshold (Ferocious, Formidable)
# -----------------------------
POWER_THRESHOLD_RE = re.compile(
    r"creatures\s+you\s+control\s+with\s+power\s+(?P<num>\d+)",
    re.IGNORECASE
)

def parse_power_threshold_condition(text: str) -> Optional[Condition]:
    m = POWER_THRESHOLD_RE.search(text)
    if not m:
        return None

    n = int(m.group("num"))
    return Condition(
        kind="power_threshold",
        subject="creatures you control",
        min_value=n
    )


# -----------------------------
# 3.7 Morbid / Revolt (event flags)
# -----------------------------
def parse_event_flag_condition(text: str) -> Optional[Condition]:
    t = text.lower()

    if "a creature died this turn" in t:
        return Condition(kind="event_flag", extra={"event": "creature_died"})

    if "a permanent you controlled left the battlefield this turn" in t:
        return Condition(kind="event_flag", extra={"event": "permanent_left"})

    return None


# ============================================================
# 4. Dispatcher
# ============================================================

CONDITION_PARSERS: List[Callable[[str], Optional[Condition]]] = [
    parse_card_type_count_condition,
    parse_threshold_condition,
    parse_card_count_condition,
    parse_domain_condition,
    parse_coven_condition,
    parse_power_threshold_condition,
    parse_event_flag_condition,
]


def parse_condition(text: str) -> Optional[Condition]:
    for parser in CONDITION_PARSERS:
        cond = parser(text)
        if cond:
            return cond
    return None

# ------------------------------------------------------------
# 1. Condition wrapper regexes
# ------------------------------------------------------------

AS_LONG_AS_RE = re.compile(
    r"\bas long as\b\s+([^,\.]+)",
    re.IGNORECASE
)

IF_RE = re.compile(
    r"\bif\b\s+([^,\.]+)",
    re.IGNORECASE
)

WHILE_RE = re.compile(
    r"\bwhile\b\s+([^,\.]+)",
    re.IGNORECASE
)

X_IS_RE = re.compile(
    r"\bx\s+is\b\s+([^,\.]+)",
    re.IGNORECASE
)

# Add more wrappers if needed
CONDITION_WRAPPERS = [
    AS_LONG_AS_RE,
    IF_RE,
    WHILE_RE,
    X_IS_RE,
]


# ------------------------------------------------------------
# 2. Normalization helper
# ------------------------------------------------------------

def normalize_condition_text(cond: str) -> str:
    cond = cond.strip().lower()

    # Remove filler prefixes
    cond = re.sub(r"^there (is|are)\s+", "", cond)
    cond = re.sub(r"^you have\s+", "", cond)
    cond = re.sub(r"^you control\s+", "", cond)
    cond = re.sub(r"^you own\s+", "", cond)
    cond = re.sub(r"^if\s+", "", cond)

    # Remove useless "that"
    cond = re.sub(r"\bthat\b\s*", "", cond)

    # Collapse whitespace
    cond = re.sub(r"\s+", " ", cond)

    return cond


# ------------------------------------------------------------
# 3. Main extraction function
# ------------------------------------------------------------

def extract_condition_text(clause: str) -> tuple[str | None, str]:
    """
    Extracts condition text from a clause and returns:
        (normalized_condition_text or None, remaining_effect_clause)

    Example:
        "this creature gets +3/+3 as long as there are seven or more cards in your graveyard"
        → ("seven or more cards in your graveyard",
           "this creature gets +3/+3")
    """

    for regex in CONDITION_WRAPPERS:
        m = regex.search(clause)
        if m:
            raw_cond = m.group(1).strip()
            normalized = normalize_condition_text(raw_cond)

            # Remove the condition part from the clause
            effect = clause[:m.start()].strip()

            return normalized, effect

    # No condition found
    return None, clause.strip()
