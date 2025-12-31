# axis2/parsing/triggers.py

import re
from axis2.schema import ( ZoneChangeEvent, DealsDamageEvent, EntersBattlefieldEvent, 
    LeavesBattlefieldEvent, CastSpellEvent, SpellFilter
)

def parse_spell_filter(text: str) -> SpellFilter:
    """
    Parses the part of a trigger condition describing the spell being cast.
    Example inputs:
      "a noncreature spell"
      "an instant or sorcery spell"
      "a creature spell"
      "an enchantment spell"
      "a spell"
    """
    t = text.lower().strip()
    f = SpellFilter()

    # -----------------------------------------
    # 1. Must-NOT-have types (detect first!)
    # -----------------------------------------
    if re.search(r"\bnoncreature\b", t):
        f.must_not_have_types.append("Creature")

    # -----------------------------------------
    # 2. Must-have types (whole-word matches)
    # -----------------------------------------
    # Instant or sorcery
    if re.search(r"\binstant or sorcery\b", t):
        f.must_have_types.extend(["Instant", "Sorcery"])

    # Single types
    elif re.search(r"\binstant spell\b", t):
        f.must_have_types.append("Instant")

    elif re.search(r"\bsorcery spell\b", t):
        f.must_have_types.append("Sorcery")

    elif re.search(r"\bcreature spell\b", t):
        f.must_have_types.append("Creature")

    elif re.search(r"\benchantment spell\b", t):
        f.must_have_types.append("Enchantment")

    elif re.search(r"\bartifact spell\b", t):
        f.must_have_types.append("Artifact")

    elif re.search(r"\bplaneswalker spell\b", t):
        f.must_have_types.append("Planeswalker")

    # -----------------------------------------
    # 3. Generic "a spell" → no type restrictions
    # -----------------------------------------
    # If none of the above matched, and "spell" is present,
    # we leave must_have_types empty.
    # This is correct for "Whenever you cast a spell".
    # -----------------------------------------

    return f

ENTERS_RE = re.compile(
    r"\bwhenever\b.*\benters\b",
    re.IGNORECASE
)

ETB_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+enters(?:\s+the battlefield)?",
    re.IGNORECASE
)

LTB_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+leaves\s+the battlefield",
    re.IGNORECASE
)

ATTACKS_RE = re.compile(
    r"\bwhenever\b.*\battacks\b",
    re.IGNORECASE
)

ZONE_CHANGE_TRIGGER_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+is\s+put\s+into\s+a?\s*(\w+)\s+from\s+the\s+(\w+)",
    re.IGNORECASE
)

DEALS_DAMAGE_RE = re.compile(
    r"(?:when|whenever)\s+(.*?)\s+deals\s+(combat\s+|noncombat\s+)?damage\s+to\s+(.*)",
    re.IGNORECASE
)

CAST_SPELL_RE = re.compile(
    r"(?:when|whenever)\s+(you|an opponent|a player|any player)\s+cast[s]?\s+(.*)",
    re.IGNORECASE
)

def parse_trigger_event(condition_text: str):
    text = condition_text.lower()

    # 1. Zone-change triggers (dies, put into graveyard, etc.)
    m = ZONE_CHANGE_TRIGGER_RE.search(text)
    if m:
        return ZoneChangeEvent(
            subject=m.group(1).strip(),
            from_zone=m.group(3).strip(),
            to_zone=m.group(2).strip()
        )

    # 2. Deals-damage triggers
    m = DEALS_DAMAGE_RE.search(text)
    if m:
        return DealsDamageEvent(
            subject=m.group(1).strip(),
            target=m.group(3).strip(),
            damage_type=(m.group(2).strip() if m.group(2) else "any")
        )

    # 3. Enters-the-battlefield
    m = ETB_RE.search(text)
    if m:
        return EntersBattlefieldEvent(subject=m.group(1).strip())

    # 4. Leaves-the-battlefield
    m = LTB_RE.search(text)
    if m:
        return LeavesBattlefieldEvent(subject=m.group(1).strip())

    # 5. Casts a spell
    m = CAST_SPELL_RE.search(text)
    if m:
        spell_filter = parse_spell_filter(m.group(2).strip())
        return CastSpellEvent(subject=m.group(1).strip(), spell_filter=spell_filter)

    # 5. Attacks
    if ATTACKS_RE.search(text):
        return "attacks"

    return None
