import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from db.connection import SessionLocal
from db.repository import Axis1Repository
from scryfall.client import ScryfallClient
from scryfall.mappers.axis1_mapper import Axis1Mapper
from services.deck_import_service import DeckImportService
from .schemas.request_schemas import DeckImportRequest

app = FastAPI(title="MTG Engine API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/import/deck")
def import_deck(req: DeckImportRequest, db: Session = Depends(get_db)):
    scry_client = ScryfallClient()
    mapper = Axis1Mapper()
    repo = Axis1Repository(db)
    service = DeckImportService(scry_client, mapper, repo)

    result = service.import_deck(req.deck_url)
    return {
        "imported_count": len(result),
        "cards": [c.card_id for c in result]
    }


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
