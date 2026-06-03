"""Parse coverage: structural 100% via fallback, semantic for known cards."""

import pytest

from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1Metadata
from axis2 import schema as a2
from axis2.compiler.card_compiler import CardCompiler
from axis2.schema import UnparsedOracleEffect


def _card(name, oracle, types=None):
    types = types or ["Instant"]
    face = Axis1Face(
        face_id="front",
        name=name,
        card_types=types,
        oracle_text=oracle,
    )
    return Axis1Card(
        card_id=name.lower().replace(" ", "-"),
        layout="normal",
        names=[name],
        faces=[face],
        characteristics=Axis1Characteristics(card_types=types),
        metadata=Axis1Metadata(),
    )


def test_structural_coverage_unknown_sentence():
    compiled = CardCompiler().compile(
        _card("Weird", "Bands with other legends of the same name.")
    )
    assert compiled.report.structural_parse_rate == 1.0
    assert compiled.report.parsed_clause_count >= 1
    # Fallback captures obscure text
    assert compiled.report.fallback_clause_count >= 1 or compiled.report.semantic_clause_count >= 1


def test_semantic_shock():
    compiled = CardCompiler().compile(
        _card("Shock", "Shock deals 2 damage to any target.")
    )
    assert compiled.report.semantic_parse_rate == 1.0
    assert any(
        isinstance(e, a2.DealDamageEffect)
        for e in compiled.axis2.faces[0].spell_effects
    )


def test_dynamic_tokens_semantic():
    oracle = (
        "Create a number of 2/2 black Zombie creature tokens equal to "
        "the number of opponents you have."
    )
    compiled = CardCompiler().compile(_card("Acererak", oracle, types=["Creature"]))
    r = compiled.report
    assert r.structural_parse_rate == 1.0
    # Should hit DynamicTokenParser when sentence is parsed in isolation;
    # full card may attach via triggered — check clause-level parse
    effects = []
    from axis2.parsing.effects import parse_effect_text
    from axis2.schema import ParseContext

    ctx = ParseContext(
        card_name="Acererak",
        primary_type="creature",
        face_name="Acererak",
        face_types=["creature"],
    )
    effects = parse_effect_text(oracle, ctx)
    assert any(isinstance(e, a2.CreateTokenEffect) for e in effects)


def test_fallback_produces_unparsed_oracle_type():
    from axis2.parsing.effects import parse_effect_text
    from axis2.schema import ParseContext

    ctx = ParseContext(
        card_name="X",
        primary_type="instant",
        face_name="X",
        face_types=["instant"],
    )
    effects = parse_effect_text(
        "Assemble the aeons and weave fate into spaghetti.", ctx
    )
    assert len(effects) == 1
    assert isinstance(effects[0], UnparsedOracleEffect)
    assert effects[0].heuristic_kind is None or isinstance(effects[0].heuristic_kind, str)
