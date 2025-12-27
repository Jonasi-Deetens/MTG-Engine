from pydantic import BaseModel

class DeckImportRequest(BaseModel):
    deck_url: str
