"""
Axis2 build pipeline — the 'effect builder wizard'.

Orchestrates parsing phases in a fixed order. Individual parsers live under
axis2/parsing/; this module only coordinates them and documents the flow.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

from axis1.schema import Axis1Card, Axis1Face
from axis2.schema import Axis2Card, Axis2Face, Axis2Characteristics

# Re-use implementation from builder module (single source of truth)
from axis2 import builder as _impl

logger = logging.getLogger(__name__)


class BuildPhase(Enum):
    """Ordered wizard steps for Axis2 card construction."""

    EXTRACT_CHARACTERISTICS = auto()
    EXTRACT_KEYWORDS = auto()
    DETECT_ABILITY_BOUNDARIES = auto()
    PARSE_ABILITY_CHUNKS = auto()
    MERGE_AXIS1_ABILITIES = auto()
    PARSE_MODES_AND_RESTRICTIONS = auto()
    EXPAND_KEYWORDS = auto()
    ADD_CASTING_OPTIONS = auto()
    VALIDATE = auto()


# Human-readable descriptions for docs / CLI (see docs/EFFECT_BUILDER_ARCHITECTURE.md)
PHASE_DESCRIPTIONS: dict[BuildPhase, str] = {
    BuildPhase.EXTRACT_CHARACTERISTICS: "PT, mana cost, types from Axis1 face",
    BuildPhase.EXTRACT_KEYWORDS: "Strip keyword lines; emit keyword-derived effects",
    BuildPhase.DETECT_ABILITY_BOUNDARIES: "Split oracle into triggered/activated/spell/static chunks",
    BuildPhase.PARSE_ABILITY_CHUNKS: "Per-chunk sentence parse via axis2/parsing/effects registry",
    BuildPhase.MERGE_AXIS1_ABILITIES: "Prefer structured abilities from Axis1 mapper when present",
    BuildPhase.PARSE_MODES_AND_RESTRICTIONS: "Modes, equip, enchant restrictions, mana abilities",
    BuildPhase.EXPAND_KEYWORDS: "Expand composite keywords (e.g. Treasure)",
    BuildPhase.ADD_CASTING_OPTIONS: "Flashback, escape, alternative costs",
    BuildPhase.VALIDATE: "validate_axis2_card consistency checks",
}


@dataclass
class BuildReport:
    card_name: str
    phases_run: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class Axis2BuildPipeline:
    """
    Public API for building Axis2Card from Axis1Card.

    Prefer this class over calling builder._parse_face directly — it documents
    the wizard steps and centralizes logging.
    """

    def __init__(self, *, verbose: bool = False):
        self.verbose = verbose

    def build(self, axis1_card: Axis1Card) -> Axis2Card:
        report = BuildReport(card_name=axis1_card.names[0] if axis1_card.names else "?")
        card = self._run(axis1_card, report)
        if report.warnings:
            logger.warning("Axis2 build warnings for %s: %s", report.card_name, report.warnings)
        return card

    def build_with_report(self, axis1_card: Axis1Card) -> tuple[Axis2Card, BuildReport]:
        report = BuildReport(card_name=axis1_card.names[0] if axis1_card.names else "?")
        return self._run(axis1_card, report), report

    def _run(self, axis1_card: Axis1Card, report: BuildReport) -> Axis2Card:
        face1: Axis1Face = axis1_card.faces[0]

        report.phases_run.append(BuildPhase.EXTRACT_CHARACTERISTICS.name)
        characteristics = _impl._extract_characteristics(axis1_card, face1)

        faces: List[Axis2Face] = []
        for f in axis1_card.faces:
            ctx = _impl._create_context(axis1_card, f)
            for phase in (
                BuildPhase.EXTRACT_KEYWORDS,
                BuildPhase.DETECT_ABILITY_BOUNDARIES,
                BuildPhase.PARSE_ABILITY_CHUNKS,
                BuildPhase.MERGE_AXIS1_ABILITIES,
                BuildPhase.PARSE_MODES_AND_RESTRICTIONS,
            ):
                report.phases_run.append(phase.name)
            face = _impl._parse_face(f, ctx)
            faces.append(face)

        report.phases_run.append(BuildPhase.EXPAND_KEYWORDS.name)
        _impl._expand_keywords(faces)

        report.phases_run.append(BuildPhase.ADD_CASTING_OPTIONS.name)
        _impl._add_special_casting_costs(axis1_card, faces)

        keywords = list(face1.keywords) + _impl.extract_keywords(face1.oracle_text or "")

        card = Axis2Card(
            card_id=axis1_card.card_id,
            oracle_id=axis1_card.oracle_id,
            set=axis1_card.set,
            collector_number=axis1_card.collector_number,
            faces=faces,
            characteristics=characteristics,
            keywords=keywords,
        )

        report.phases_run.append(BuildPhase.VALIDATE.name)
        from axis2.validation import validate_axis2_card

        errors = validate_axis2_card(card)
        if errors:
            report.warnings.extend(errors)

        logger.debug(
            "Built Axis2Card %s phases=%s spell_effects=%s",
            report.card_name,
            report.phases_run,
            sum(len(f.spell_effects) for f in faces),
        )
        return card
