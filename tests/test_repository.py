from db.repository import Axis1Repository
from axis1.schema import Axis1Card
from sqlalchemy.orm import Session

def test_repository_save_and_get(db_session: Session):
    """Test saving and retrieving an Axis1 card."""

    repo = Axis1Repository(db_session)

    card = Axis1Card(
        card_id="123",
        oracle_id="oracle-123",
        layout="normal",
        names=["Test Card"],
        faces=[],
        characteristics={"mana_cost": "{1}{G}", "mana_value": 2},
    )

    repo.save(card)
    loaded = repo.get_by_id("123")

    assert loaded.card_id == "123"
    assert loaded.oracle_id == "oracle-123"
