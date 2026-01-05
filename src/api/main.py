import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db.connection import SessionLocal, engine
from db.models import Base
from db.repository import Axis1Repository
from scryfall.client import ScryfallClient
from scryfall.mappers.axis1_mapper import Axis1Mapper
from scryfall.services.deck_import_service import DeckImportService
from .schemas.request_schemas import DeckImportRequest
from .routes import auth, cards, abilities

# Create database tables on startup
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"WARNING: Could not create database tables: {e}")

app = FastAPI(
    title="MTG Engine API",
    description="Magic: The Gathering card engine API",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://172.21.0.4:3000",  # Docker network IP
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(abilities.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "MTG Engine API"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


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
