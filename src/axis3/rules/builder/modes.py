# axis3/rules/modes.py

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import re

from axis3.translate.compilers.effect_compiler import compile_effect
from axis3.abilities.targeting.targeting_rules import TargetingRules


# ------------------------------------------------------------
# Axis3 Mode Dataclass
# ------------------------------------------------------------

@dataclass
class Axis3Mode:
    """
    A single mode of a modal spell or ability.
    Contains:
      - text: the raw text of the mode
      - effects: list of compiled Axis3Effect objects
      - targeting: optional targeting rules
    """
    text: str
    effects: List[object] = field(default_factory=list)
    targeting: Optional[TargetingRules] = None


# ------------------------------------------------------------
# Modal Header Pattern
# ------------------------------------------------------------

MODAL_HEADER = re.compile(
    r"choose\s+(one|two|one or more|any number)\s*—",
    re.IGNORECASE
)


# ------------------------------------------------------------
# Axis3 Modal Parser
# ------------------------------------------------------------

def parse_modes(oracle_text: str) -> Tuple[Optional[str], List[Axis3Mode]]:
    """
    Axis3 modal parser.
    Returns:
        (mode_choice, modes)
    where:
        mode_choice: "one", "two", "one or more", "any number"
        modes: list of Axis3Mode objects
    """

    if not oracle_text:
        return None, []

    # Detect modal header
    m = MODAL_HEADER.search(oracle_text)
    if not m:
        return None, []

    mode_choice = m.group(1).lower()

    # Split modes by bullet or dash
    parts = re.split(r"•|- ", oracle_text)
    mode_texts = [p.strip() for p in parts[1:] if p.strip()]

    modes: List[Axis3Mode] = []

    for text in mode_texts:
        # Compile effects for this mode
        # A mode may contain multiple sentences → split by period
        sentences = [s.strip() for s in re.split(r"[.;]", text) if s.strip()]

        effects = []
        for sentence in sentences:
            eff = compile_effect(sentence)
            if isinstance(eff, list):
                effects.extend(eff)
            else:
                effects.append(eff)

        # Targeting rules can be added later (Axis3 targeting system)
        mode = Axis3Mode(
            text=text,
            effects=effects,
            targeting=None
        )
        modes.append(mode)

    return mode_choice, modes
