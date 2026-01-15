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
from .routes import auth, cards, abilities, collections, decks, engine

# Create database tables on startup
try:
    Base.metadata.create_all(bind=engine)
    # Run migration for custom lists
    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            # Add list_id column if it doesn't exist
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='deck_cards' AND column_name='list_id'
                    ) THEN
                        ALTER TABLE deck_cards ADD COLUMN list_id INTEGER;
                        CREATE INDEX IF NOT EXISTS ix_deck_cards_list_id ON deck_cards(list_id);
                    END IF;
                END $$;
            """))
            # Create deck_custom_lists table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS deck_custom_lists (
                    id SERIAL PRIMARY KEY,
                    deck_id INTEGER NOT NULL,
                    name VARCHAR NOT NULL,
                    position INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
                );
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_deck_custom_lists_deck_id ON deck_custom_lists(deck_id);"))
            # Add foreign key constraint if it doesn't exist
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE table_name='deck_cards' AND constraint_name='fk_deck_cards_list_id'
                    ) THEN
                        ALTER TABLE deck_cards 
                        ADD CONSTRAINT fk_deck_cards_list_id 
                        FOREIGN KEY (list_id) REFERENCES deck_custom_lists(id) ON DELETE SET NULL;
                    END IF;
                END $$;
            """))
        print("✓ Custom lists migration applied")
    except Exception as mig_e:
        print(f"WARNING: Could not apply custom lists migration: {mig_e}")
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
app.include_router(collections.router)
app.include_router(decks.router)
app.include_router(engine.router)


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
