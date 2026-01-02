# axis2/parsing/triggers/utils.py

"""Shared utilities for trigger parsing"""
from axis2.schema import SpellFilter
import re

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

    return f

