"""
Bulk import all Scryfall cards into PostgreSQL using Axis1Mapper.
"""

import time
import requests
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scryfall.mappers.axis1_mapper import Axis1Mapper
from db.repository import Axis1Repository
from db.models import Base


SCRYFALL_BULK_URL = "https://api.scryfall.com/bulk-data/default-cards"


def download_bulk_file():
    """Fetch the URL of the Scryfall bulk card file."""
    print("Fetching Scryfall bulk metadata...")
    resp = requests.get(SCRYFALL_BULK_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["download_uri"]


def load_bulk_cards(download_url): 
    print("Downloading bulk card data...") 
    resp = requests.get(download_url) 
    resp.raise_for_status() 
    return resp.json()


def main():
    print("Starting bulk import...")

    # 1. Get bulk file URL
    download_url = download_bulk_file()
    print(f"Bulk file URL: {download_url}")

    # 2. Setup DB
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5433/mtg")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    session = SessionLocal()
    repo = Axis1Repository(session)
    mapper = Axis1Mapper()

    count = 0

    cards = load_bulk_cards(download_url)

    for card_json in cards:
        try:
            # print(f"Processing card: {card_json['name']}")
            axis1_card = mapper.map(card_json)
            # print(f"Axis1 card: {axis1_card}")
            repo.save(axis1_card)
            # print(f"Saved card: {axis1_card.card_id}")
            count += 1

            if count % 500 == 0:
                print(f"Imported {count} cards...")
                session.commit()

        except Exception as e:
            print(f"Error processing card: {e}")


if __name__ == "__main__":
    main()
