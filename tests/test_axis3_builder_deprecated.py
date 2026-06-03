import warnings

import pytest

from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1Metadata
from axis3.cards.card_builder import Axis3CardBuilder


def test_axis3_card_builder_import_path():
    face = Axis1Face(
        face_id="front",
        name="Shock",
        card_types=["Instant"],
        oracle_text="Shock deals 2 damage to any target.",
    )
    axis1 = Axis1Card(
        card_id="s",
        layout="normal",
        names=["Shock"],
        faces=[face],
        characteristics=Axis1Characteristics(card_types=["Instant"]),
        metadata=Axis1Metadata(),
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        card = Axis3CardBuilder.build(axis1)
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
    assert card.name == "Shock"
    assert card.metadata.get("axis2_built") is True
