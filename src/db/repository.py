from sqlalchemy.orm import Session
from axis1.schema import Axis1Card
from .models import Axis1CardModel


class Axis1Repository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, card: Axis1Card) -> Axis1CardModel:
        data = card.dict()
        model = Axis1CardModel(
            card_id=data["card_id"],
            oracle_id=data.get("oracle_id"),
            set_code=data.get("set"),
            collector_number=data.get("collector_number"),
            layout=data.get("layout"),
            name=data["names"][0] if data.get("names") else None,
            lang=data.get("lang"),
            axis1_json=data,
        )
        self.db.merge(model)  # upsert-like behavior
        self.db.commit()
        return model

    def get_by_id(self, card_id: str) -> Axis1CardModel:
        return self.db.query(Axis1CardModel).filter_by(card_id=card_id).first()
