"""
End-to-end card compilation: oracle text → Axis2 effects → runtime-ready structures.

Parsing strategy (not one giant regex):
  1. Segment oracle text into ability chunks (syntactic markers + card type)
  2. Per sentence, run registry of small regex parsers (axis2/parsing/effects/)
  3. Keywords / triggers / static / replacement have dedicated modules
  4. Unparsed clauses are reported for coverage tracking

Axis3 EffectExecutor runs the structured Axis2 output — it does not re-parse English.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from axis1.schema import Axis1Card
from axis2.build_pipeline import Axis2BuildPipeline
from axis2.schema import Axis2Card, Effect, ParseContext, UnparsedOracleEffect
from axis2.parsing.effects import parse_effect_text
from axis2.parsing.effects.utils import split_effect_sentences


@dataclass
class ParseReport:
    card_name: str
    oracle_text: str
    parsed_clause_count: int = 0
    semantic_clause_count: int = 0
    fallback_clause_count: int = 0
    unparsed_clauses: List[str] = field(default_factory=list)
    effect_count: int = 0

    @property
    def fully_parsed(self) -> bool:
        return len(self.unparsed_clauses) == 0

    @property
    def structural_parse_rate(self) -> float:
        """100% when fallback parser is enabled — every clause becomes an Effect."""
        total = self.parsed_clause_count + len(self.unparsed_clauses)
        if total == 0:
            return 1.0
        return self.parsed_clause_count / total

    @property
    def semantic_parse_rate(self) -> float:
        """Share of clauses parsed by specialized regex parsers (not fallback)."""
        total = self.parsed_clause_count + len(self.unparsed_clauses)
        if total == 0:
            return 1.0
        return self.semantic_clause_count / total

    parse_rate = structural_parse_rate


@dataclass
class CompiledCard:
    axis1: Axis1Card
    axis2: Axis2Card
    report: ParseReport


class CardCompiler:
    """Compile a card from Axis1 to Axis2 with parse coverage metadata."""

    def __init__(self, builder: Optional[Axis2BuildPipeline] = None):
        self.builder = builder or Axis2BuildPipeline()

    def compile(self, axis1: Axis1Card, game_state: Any = None) -> CompiledCard:
        axis2 = self.builder.build(axis1)
        report = self._build_parse_report(axis1, axis2)
        return CompiledCard(axis1=axis1, axis2=axis2, report=report)

    def _build_parse_report(self, axis1: Axis1Card, axis2: Axis2Card) -> ParseReport:
        face = axis1.faces[0]
        oracle = (face.oracle_text or "").strip()
        name = axis1.names[0] if axis1.names else "unknown"

        if not oracle:
            return ParseReport(
                card_name=name,
                oracle_text="",
                parsed_clause_count=0,
                semantic_clause_count=0,
                fallback_clause_count=0,
                effect_count=self._count_effects(axis2),
            )

        clean_types = [t for t in face.card_types if t not in face.supertypes]
        ctx = ParseContext(
            card_name=name,
            primary_type=clean_types[0].lower() if clean_types else "unknown",
            face_name=face.name,
            face_types=[t.lower() for t in face.card_types],
            is_spell_text=any(t in face.card_types for t in ("Instant", "Sorcery")),
        )

        unparsed: List[str] = []
        parsed_count = 0
        semantic_count = 0
        fallback_count = 0

        for sentence in split_effect_sentences(oracle):
            s = sentence.strip()
            if not s:
                continue
            effects = parse_effect_text(s, ctx)
            if effects:
                parsed_count += 1
                if any(isinstance(e, UnparsedOracleEffect) for e in effects):
                    fallback_count += 1
                else:
                    semantic_count += 1
            else:
                unparsed.append(s)

        effect_count = self._count_effects(axis2)

        return ParseReport(
            card_name=name,
            oracle_text=oracle,
            parsed_clause_count=parsed_count,
            semantic_clause_count=semantic_count,
            fallback_clause_count=fallback_count,
            unparsed_clauses=unparsed,
            effect_count=effect_count,
        )

    @staticmethod
    def _count_effects(axis2: Axis2Card) -> int:
        n = 0
        for face in axis2.faces:
            n += len(face.spell_effects)
            for aa in face.activated_abilities:
                n += len(aa.effects)
            for trig in face.triggered_abilities:
                n += len(trig.effects)
            n += len(face.static_effects)
            n += len(face.continuous_effects)
            n += len(face.replacement_effects)
            for mode in face.modes:
                n += len(mode.effects)
        return n
