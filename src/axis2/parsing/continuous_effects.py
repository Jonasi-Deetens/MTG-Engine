# axis2/parsing/continuous_effects.py

import re
from typing import List, Optional

from axis2.schema import (
    ContinuousEffect, PTExpression,
    ColorChangeData, TypeChangeData, 
    CardTypeCountCondition,
    ParseContext,
    DynamicValue,
    GrantedAbility,
    RuleChangeData
)
from axis2.parsing.subject import subject_from_text
from axis2.parsing.conditions import parse_condition, extract_condition_text
# -----------------------------
# Regex patterns
# -----------------------------

PT_GETS_RE = re.compile(r"gets\s+([+\-]?\w+)\/([+\-]?\w+)", re.IGNORECASE)
HAS_ABILITY_RE = re.compile(r"has\s+(.+)", re.IGNORECASE)
GAINS_ABILITY_RE = re.compile(r"gains?\s+(.+)", re.IGNORECASE)
IS_COLOR_RE = re.compile(r"is\s+([a-z\s,]+)", re.IGNORECASE)

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

COLOR_WORD_TO_SYMBOL = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

ABILITY_KEYWORDS = {
    "flying", "first strike", "double strike", "vigilance", "lifelink",
    "trample", "deathtouch", "haste", "reach", "menace", "hexproof",
    "indestructible", "ward"
}

CLAUSE_BOUNDARIES = [
    " with base power and toughness ",
    " with base power & toughness ",
    " and has ",
    " and have ",
    " and gains ",
    " and gain ",
    " and it loses ",
    " and loses ",
]

# -----------------------------
# Helpers
# -----------------------------

def split_continuous_clauses(text: str) -> list[str]:
    t = text.strip()
    lower = t.lower()

    # First pass: split using your explicit CLAUSE_BOUNDARIES
    clauses = [(t, lower)]

    for b in CLAUSE_BOUNDARIES:
        new_clauses = []
        b_lower = b.lower()
        for orig, low in clauses:
            idx = low.find(b_lower)
            if idx == -1:
                new_clauses.append((orig, low))
                continue

            before_orig = orig[:idx].strip(" ,.")
            after_orig = orig[idx + len(b):].strip(" ,.")
            before_low = low[:idx].strip(" ,.")
            after_low = low[idx + len(b):].strip(" ,.")

            if before_orig:
                new_clauses.append((before_orig, before_low))
            if after_orig:
                boundary_prefix = b.strip()
                new_clauses.append(
                    (boundary_prefix + " " + after_orig,
                     boundary_prefix.lower() + " " + after_low)
                )
        clauses = new_clauses

    # SECOND PASS: split on "and ..." verb phrases
    final_clauses = []
    for orig, low in clauses:
        parts = re.split(
            r'\b(?:and|, and)\b(?=\s+(has|have|is|are|loses|gains|gets|becomes))',
            orig,
            flags=re.I
        )
        for p in parts:
            p = p.strip(" ,.")
            if p:
                final_clauses.append(p)

    return final_clauses

def _guess_applies_to(text: str) -> str:
    lower = text.lower().strip()
    lower = lower.rstrip(".,;:")
    lower = " ".join(lower.split())

    if lower.startswith("target "):
        return "target"

    if lower.startswith("enchanted creature"):
        return "enchanted_creature"
    if lower.startswith("equipped creature"):
        return "equipped_creature"
    if lower.startswith("creatures you control"):
        return "creatures_you_control"
    if lower.startswith("creature you control"):
        return "creature_you_control"
    if lower.startswith("creatures you don't control"):
        return "creatures_you_dont_control"
    if lower.startswith("this creature"):
        return "this_creature"
    if lower.startswith("this permanent"):
        return "this_permanent"

    return None

def _parse_pt_mod(text: str) -> Optional[PTExpression]:
    m = PT_GETS_RE.search(text)
    if not m:
        return None
    p = m.group(1).lstrip("+")
    t = m.group(2).lstrip("+")
    return PTExpression(power=p, toughness=t)


def _parse_abilities(text: str) -> Optional[list[GrantedAbility]]:
    lower = text.lower()

    # Extract the part after "has ..." or "gains ..."
    if "has " in lower:
        m = HAS_ABILITY_RE.search(lower)
        if not m:
            return None
        ability_part = m.group(1)
    elif "gains " in lower or "gain " in lower:
        m = GAINS_ABILITY_RE.search(lower)
        if not m:
            return None
        ability_part = m.group(1)
    else:
        return None

    # Normalize separators
    ability_part = ability_part.replace(", and ", ", ")
    ability_part = ability_part.replace(" and ", ", ")
    raw = [a.strip().rstrip(".") for a in ability_part.split(",")]

    abilities: list[GrantedAbility] = []

    for a in raw:
        a = re.sub(r"\s+until.*$", "", a)

        # Ward {N}
        print(f"Parsing ability RAW A: {a}")
        m = re.match(r"ward\s*\{(\d+)\}", a)
        if m:
            value = int(m.group(1))
            abilities.append(GrantedAbility(kind="ward", value=value))
            continue

        # Simple keyword abilities
        if a in ABILITY_KEYWORDS:
            abilities.append(GrantedAbility(kind=a))
            continue

    return abilities or None

def _parse_color_change(text: str) -> Optional[ColorChangeData]:
    lower = text.lower()

    if "is all colors" in lower:
        return ColorChangeData(set_colors=["W", "U", "B", "R", "G"])

    m = IS_COLOR_RE.search(lower)
    if not m:
        return None

    words = m.group(1).replace(",", " ").split()
    colors = [COLOR_WORD_TO_SYMBOL[w] for w in words if w in COLOR_WORD_TO_SYMBOL]
    if not colors:
        return None

    if "in addition to its other colors" in lower:
        return ColorChangeData(add_colors=colors)
    return ColorChangeData(set_colors=colors)


def _parse_type_change(text: str) -> Optional[TypeChangeData]:
    lower = text.lower()
    if " is a " in lower:
        after = lower.split(" is a ", 1)[1]
    elif " is an " in lower:
        after = lower.split(" is an ", 1)[1]
    elif " is " in lower:
        after = lower.split(" is ", 1)[1]
    else:
        return None

    # Stop at common clause boundaries
    for stop in [" with base power", " and has ", " and it loses", " and loses "]:
        idx = after.find(stop)
        if idx != -1:
            after = after[:idx]
            break

    after = after.strip(" ,.")
    words = after.split()

    known_types = {"creature", "artifact", "enchantment", "land", "planeswalker", "instant", "sorcery"}
    types = [w for w in words if w in known_types]
    # everything else we treat as subtypes for now
    subtypes = [w for w in words if w not in known_types]

    if not types and not subtypes:
        return None

    # you might want separate fields later; for now, pack them
    return TypeChangeData(set_types=types + subtypes)

FOR_EACH_COUNTER_RE = re.compile(
    r"for each (?P<counter>[\w\+\-\/]+) counter on (?P<subject>[^\.]+)",
    re.IGNORECASE
)

def parse_dynamic_counter_clause(text: str, ctx: ParseContext):
    m = FOR_EACH_COUNTER_RE.search(text)
    if not m:
        return None

    counter_type = m.group("counter").lower().strip()
    subj_text = m.group("subject").strip()

    # Convert subject text ("this creature") into a Subject object
    subject = subject_from_text(subj_text, ctx)

    return DynamicValue(
        kind="counter_count",
        counter_type=counter_type,
        subject=subject
    )

BASE_PT_RE = re.compile(
    r"base power and toughness\s+(\d+)\/(\d+)", re.IGNORECASE
)

def _parse_base_pt_set(text: str) -> Optional[PTExpression]:
    m = BASE_PT_RE.search(text)
    if not m:
        return None
    return PTExpression(power=m.group(1), toughness=m.group(2))

LOSES_ALL_RE = re.compile(r"loses\s+all\s+other?\s+(abilities|card types|creature types)", re.I)

def _parse_loss_effects(text: str, applies_to: str, condition) -> list[ContinuousEffect]:
    lower = text.lower()
    effects: list[ContinuousEffect] = []

    # Lose all abilities (keep this as-is, it's precise and good)
    if "loses all abilities" in lower or "loses all other abilities" in lower:
        effects.append(
            ContinuousEffect(
                kind="ability_remove_all",
                applies_to=applies_to,
                condition=condition,
                text=text,
            )
        )

    # Lose card types if they appear in the same clause
    if "card types" in lower:
        effects.append(
            ContinuousEffect(
                kind="type_remove_all",
                applies_to=applies_to,
                condition=condition,
                text=text,
            )
        )

    # Lose creature types if they appear in the same clause
    if "creature types" in lower:
        effects.append(
            ContinuousEffect(
                kind="subtype_remove_all",
                applies_to=applies_to,
                condition=condition,
                text=text,
            )
        )

    return effects

def _parse_cant_be_blocked_by(clause: str):
    m = re.search(
        r"(?:can't|cannot) be blocked by ([a-z]+) creatures",
        clause,
        re.I
    )
    if m:
        color = m.group(1).lower()
        return {"colors": [color]}
    return None

PROT_RE = re.compile(
    r"protection from ([^\n\.]+)",   # stop at newline or period
    re.I
)

def _parse_protection(text: str, applies_to: str, duration: str):
    m = PROT_RE.search(text)
    if not m:
        return None

    raw = m.group(1).lower()
    parts = re.split(r",|and", raw)

    colors = []
    for p in parts:
        clean = p.strip()
        if clean.startswith("from "):
            clean = clean[5:]
        if clean:
            colors.append(clean)

    return ContinuousEffect(
        kind="grant_protection",
        applies_to=applies_to,
        protection_from=colors,
        duration=duration,
        text=text,
    )

def _parse_rule_change(text: str) -> Optional[RuleChangeData]:
    lower = text.lower()

    # Coalition Flag / Flagbearer pattern
    if "must choose at least one flagbearer" in lower:
        return RuleChangeData(
            kind="targeting_requirement",
            requires_flagbearer=True,
            controller="opponent"
        )

    # Generalized "must choose this creature if able"
    if "must choose" in lower and "if able" in lower:
        return RuleChangeData(
            kind="targeting_requirement",
            requires_this=True
        )

    # Generalized "must choose a creature with X"
    m = re.search(r"must choose .* (creature.*) if able", lower)
    if m:
        return RuleChangeData(
            kind="targeting_requirement",
            requires_filter=m.group(1)
        )

    return None

# -----------------------------
# Main parser
# -----------------------------

def parse_continuous_effects(text: str, ctx: ParseContext) -> List[ContinuousEffect]:
    effects = []
    if not text:
        return effects

    # 1b. Split into semantic clauses 
    clauses = split_continuous_clauses(text)
    current_subject = None

    for clause in clauses:
        # 1. Conditional wrapper
        condition = None
        condition, clause = extract_condition_text(clause)
        # Try to parse structured card-type-count conditions (Delirium-like)
        structured = parse_condition(condition) if condition else None
        print(f"Structured condition: {structured}")
        if structured:
            condition = structured

        applies_to = _guess_applies_to(clause)

        if applies_to is None:
            applies_to = current_subject
        else:
            current_subject = applies_to

        # Detect duration
        duration = None
        if "until end of turn" in clause.lower():
            duration = "until_end_of_turn"
        elif "this turn" in clause.lower():
            duration = "this_turn"
        elif "until your next turn" in clause.lower():
            duration = "until_your_next_turn"
        elif "until your next upkeep" in clause.lower():
            duration = "until_your_next_upkeep"

        # 2. P/T modification
        pt = _parse_pt_mod(clause)
        if pt:
            effect = ContinuousEffect(
                kind="pt_mod",
                applies_to=applies_to,
                pt_value=pt,
                condition=condition,
                text=clause,
                duration=duration,
            )

            # NEW: detect dynamic scaling like "for each valor counter on this creature"
            dynamic = parse_dynamic_counter_clause(clause, ctx)
            if dynamic:
                effect.dynamic = dynamic

            effects.append(effect)

        # 2b. Base P/T setting (new) 
        base_pt = _parse_base_pt_set(clause) 
        if base_pt: effects.append( 
            ContinuousEffect( 
                kind="pt_set", 
                applies_to=applies_to, 
                pt_value=base_pt, 
                condition=condition, 
                text=clause, 
                duration=duration,
            ) 
        )
        # 3. Ability granting
        abilities = _parse_abilities(clause)
        if abilities:
            effects.append(
                ContinuousEffect(
                    kind="grant_ability",
                    applies_to=applies_to,
                    abilities=abilities,
                    condition=condition,
                    text=clause,
                    duration=duration,
                )
            )

        # 3b. Ability / type loss (new) 
        loss_effects = _parse_loss_effects(clause, applies_to, condition)
        effects.extend(loss_effects)

        # 4. Color change
        color_change = _parse_color_change(clause)
        if color_change:
            effects.append(
                ContinuousEffect(
                    kind="color_set" if color_change.set_colors else "color_add",
                    applies_to=applies_to,
                    color_change=color_change,
                    condition=condition,
                    text=clause,
                    duration=duration,
                )
            ) 

        # 4.5 Rule‑changing continuous effects (NEW)
        rule_change = _parse_rule_change(clause)
        if rule_change:
            effects.append(
                ContinuousEffect(
                    kind="rule_change",
                    applies_to=None,
                    rule_change=rule_change,
                    condition=condition,
                    text=clause,
                    duration=duration,
                )
            )
            continue  # IMPORTANT: prevent misclassification as type_change


        # 5. Type change
        type_change = _parse_type_change(clause)
        if type_change:
            effects.append(
                ContinuousEffect(
                    kind="type_set",
                    applies_to=applies_to,
                    type_change=type_change,
                    condition=condition,
                    text=clause,
                    duration=duration,
                )
            )

        # 6. Cant be blocked by
        restriction = _parse_cant_be_blocked_by(clause)
        if restriction:
            effects.append(
                ContinuousEffect(
                    kind="cant_be_blocked_by",
                    applies_to=applies_to,
                    condition=condition,
                    text=clause,
                    color_change=None,
                    type_change=None,
                    abilities=None,
                    pt_value=None,
                    dynamic=None,
                    protection_from=None,
                    control_change=None,
                    cost_change=None,
                    rule_change=None,
                    # store the restriction
                    restriction=restriction,
                    duration=duration,
                )
            )

        # 7. Protection from
        protection = _parse_protection(clause, applies_to=applies_to, duration=duration)
        if protection:
            effects.append(protection)


    # 6. Fallback: unknown continuous effect

    return effects