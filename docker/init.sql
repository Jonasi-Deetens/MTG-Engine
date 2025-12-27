CREATE TABLE IF NOT EXISTS axis1_cards (
    card_id          TEXT PRIMARY KEY,
    oracle_id        TEXT,
    set_code         TEXT,
    collector_number TEXT,
    layout           TEXT,
    name             TEXT,
    lang             TEXT,
    axis1_json       JSONB
);

CREATE INDEX IF NOT EXISTS idx_axis1_oracle_id
    ON axis1_cards (oracle_id);

CREATE INDEX IF NOT EXISTS idx_axis1_set_code
    ON axis1_cards (set_code);

CREATE INDEX IF NOT EXISTS idx_axis1_name
    ON axis1_cards (name);
