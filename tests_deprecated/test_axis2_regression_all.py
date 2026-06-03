import json
import pytest
from deepdiff import DeepDiff
from sqlalchemy import text

from axis1.schema import Axis1Card
from axis2.builder import Axis2Builder
from db.repository import Axis2TestRepository


def diff_json(a, b):
    return DeepDiff(a, b, ignore_order=True)


def axis2_to_json(axis2_card):
    if hasattr(axis2_card, "model_dump"):
        return axis2_card.model_dump()
    if hasattr(axis2_card, "dict"):
        return axis2_card.dict()

    from dataclasses import is_dataclass, asdict
    if is_dataclass(axis2_card):
        return asdict(axis2_card)

    if hasattr(axis2_card, "__dict__"):
        return axis2_card.__dict__

    raise TypeError("Axis2Card cannot be serialized")


def load_axis1_by_name(pg_session, name: str) -> Axis1Card:
    row = pg_session.execute(
        text("""
            SELECT axis1_json
            FROM axis1_cards
            WHERE axis1_json->'faces'->0->>'name' = :name
            LIMIT 1
        """),
        {"name": name}
    ).fetchone()

    if not row:
        raise RuntimeError(f"No Axis1 card found for name={name!r}")

    return Axis1Card(**row.axis1_json)


def test_axis2_regression_all(pg_session):
    """
    Runs Axis2 regression tests for ALL saved golden cards.
    """

    repo = Axis2TestRepository(pg_session)
    saved_cards = pg_session.execute(
        text("SELECT name, axis2_json FROM axis2_test_cards ORDER BY name")
    ).fetchall()

    if not saved_cards:
        pytest.skip("No saved Axis2 test cards found in axis2_test_cards")

    failures = []

    for row in saved_cards:
        name = row.name
        saved_json = row.axis2_json

        # Load Axis1
        axis1_card = load_axis1_by_name(pg_session, name)

        # Build fresh Axis2
        axis2_card = Axis2Builder.build(axis1_card)
        current_json = axis2_to_json(axis2_card)

        # Compare
        diff = diff_json(saved_json, current_json)
        if diff:
            failures.append((name, diff))

    # Report failures
    if failures:
        print("\n=== AXIS2 REGRESSION FAILURES ===")
        for name, diff in failures:
            print(f"\n--- {name} ---")
            print(json.dumps(diff, indent=2))
        raise AssertionError(f"{len(failures)} Axis2 regression(s) detected")

    print("\nAll Axis2 golden files match — full suite OK")
