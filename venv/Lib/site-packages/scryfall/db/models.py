from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Axis1CardModel(Base):
    __tablename__ = "axis1_cards"

    card_id = Column(String, primary_key=True)
    oracle_id = Column(String, index=True)
    set_code = Column(String, index=True)
    collector_number = Column(String)
    layout = Column(String)
    name = Column(String, index=True)
    lang = Column(String)
    axis1_json = Column(JSON)  # store full Axis1Card dict
