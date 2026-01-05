# axis2/parsing/continuous_effects/utils.py

"""Shared utilities for continuous effect parsing"""
import re
from typing import Optional
from .patterns import CLAUSE_BOUNDARIES

def split_continuous_clauses(text: str) -> list[str]:
    """Split text into semantic clauses for continuous effects"""
    t = text.strip()
    lower = t.lower()

    # First pass: split using explicit CLAUSE_BOUNDARIES
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

    # SECOND PASS: split on "and ..." verb phrases and comma-separated clauses
    final_clauses = []
    for orig, low in clauses:
        parts = re.split(
            r'\b(?:and|, and|,)\b(?=\s+(has|have|is|are|loses|gains|gets|becomes))',
            orig,
            flags=re.I
        )
        for p in parts:
            p = p.strip(" ,.")
            if p:
                final_clauses.append(p)

    return final_clauses

def guess_applies_to(text: str) -> Optional[str]:
    """Guess what subject this effect applies to based on text"""
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

def detect_duration(text: str) -> Optional[str]:
    """Detect duration from text"""
    lower = text.lower()
    if "until end of turn" in lower:
        return "until_end_of_turn"
    elif "this turn" in lower:
        return "this_turn"
    elif "until your next turn" in lower:
        return "until_your_next_turn"
    elif "until your next upkeep" in lower:
        return "until_your_next_upkeep"
    return None

