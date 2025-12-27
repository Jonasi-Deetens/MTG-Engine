mtg_engine/
│
├── docker/
│   ├── Dockerfile.api              # Python app container
│   ├── Dockerfile.db               # Optional custom Postgres image
│   └── init.sql                    # Optional DB initialization script
│
├── docker-compose.yml              # Orchestration for API + Postgres
│
├── requirements.txt                # Python dependencies
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Environment variables, DB URL, Scryfall URL
│   │   └── logging_config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py           # SQLAlchemy engine/session
│   │   ├── models.py               # SQLAlchemy models for Axis1
│   │   └── repository.py           # Insert/update/fetch logic
│   │
│   ├── scryfall/
│   │   ├── __init__.py
│   │   ├── client.py               # Fetch from Scryfall API
│   │   ├── deck_fetcher.py         # Fetch decklists, bulk data, etc.
│   │   └── mappers/
│   │       ├── __init__.py
│   │       └── axis1_mapper.py     # Convert Scryfall JSON → Axis1 schema
│   │
│   ├── axis1/
│   │   ├── __init__.py
│   │   ├── schema.py               # Axis1 dataclasses / Pydantic models
│   │   └── validator.py            # Validate Axis1 objects
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── deck_import_service.py  # High-level workflow: fetch → map → save
│   │   └── card_import_service.py  # Single-card import
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI/Flask entrypoint
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── deck_routes.py      # Endpoints: /import/deck, /cards
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── request_schemas.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── http.py                 # Requests wrapper
│       ├── parsing.py              # Type-line parsing, etc.
│       └── helpers.py
│
└── tests/
    ├── __init__.py
    ├── test_axis1_mapping.py
    ├── test_scryfall_client.py
    ├── test_db_integration.py
    └── test_deck_import_service.py
