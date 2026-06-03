"""Axis2 build pipeline wizard tests."""

from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1Metadata
from axis2 import schema as a2
from axis2.build_pipeline import Axis2BuildPipeline, BuildPhase


def _shock():
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
        card_id="shock",
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


def test_pipeline_runs_all_phases():
    card, report = Axis2BuildPipeline().build_with_report(_shock())
    assert BuildPhase.VALIDATE.name in report.phases_run
    assert BuildPhase.EXTRACT_KEYWORDS.name in report.phases_run
    assert BuildPhase.MERGE_AXIS1_ABILITIES.name in report.phases_run
    assert BuildPhase.PARSE_MODES_AND_RESTRICTIONS.name in report.phases_run
    assert card.faces[0].spell_effects


def test_pipeline_matches_builder():
    axis1 = _shock()
    from axis2.builder import Axis2Builder

    a = Axis2BuildPipeline().build(axis1)
    b = Axis2Builder.build(axis1)
    assert len(a.faces[0].spell_effects) == len(b.faces[0].spell_effects)
    assert any(isinstance(e, a2.DealDamageEffect) for e in a.faces[0].spell_effects)


def test_integration_loader():
    from axis3.integration.runtime_loader import compile_axis2, create_runtime_object
    from axis3.state.game_state import GameState, PlayerState
    from axis3.state.zones import ZoneType
    from axis3.engine.stack.stack import Stack

    axis1 = _shock()
    axis2 = compile_axis2(axis1)
    gs = GameState(players=[PlayerState(id=0)], objects={}, stack=Stack())
    rt = create_runtime_object(axis1, axis2, 0, ZoneType.LIBRARY, gs)
    assert rt.axis2_card is not None
    assert rt.axis1_card is not None
