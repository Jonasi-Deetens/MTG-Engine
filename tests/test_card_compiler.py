"""Card compiler: oracle → Axis2 → executable effect objects."""

import pytest

from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1Metadata
from axis2 import schema as a2
from axis2.compiler.card_compiler import CardCompiler


def _shock_axis1():
    face = Axis1Face(
        face_id="front",
        name="Shock",
        mana_cost="{R}",
        mana_value=1,
        colors=["R"],
        card_types=["Instant"],
        oracle_text="Shock deals 2 damage to any target.",
    )
    return Axis1Card(
        card_id="shock-test",
        layout="normal",
        names=["Shock"],
        faces=[face],
        characteristics=Axis1Characteristics(
            mana_cost="{R}",
            mana_value=1,
            colors=["R"],
            card_types=["Instant"],
        ),
        metadata=Axis1Metadata(),
    )


def test_instant_spell_effects_on_axis2_face():
    compiled = CardCompiler().compile(_shock_axis1())
    spell_effects = compiled.axis2.faces[0].spell_effects
    assert any(isinstance(e, a2.DealDamageEffect) for e in spell_effects)


def test_parse_report_fully_parsed_shock():
    compiled = CardCompiler().compile(_shock_axis1())
    assert compiled.report.fully_parsed
    assert compiled.report.effect_count >= 1
