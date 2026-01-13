-- Migration script to add custom lists functionality
-- Run this in your PostgreSQL database

-- Add list_id column to deck_cards if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='deck_cards' AND column_name='list_id'
    ) THEN
        ALTER TABLE deck_cards ADD COLUMN list_id INTEGER;
        CREATE INDEX IF NOT EXISTS ix_deck_cards_list_id ON deck_cards(list_id);
        RAISE NOTICE 'Added list_id column to deck_cards';
    ELSE
        RAISE NOTICE 'list_id column already exists';
    END IF;
END $$;

-- Create deck_custom_lists table if it doesn't exist
CREATE TABLE IF NOT EXISTS deck_custom_lists (
    id SERIAL PRIMARY KEY,
    deck_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);

-- Create index if it doesn't exist
CREATE INDEX IF NOT EXISTS ix_deck_custom_lists_deck_id ON deck_custom_lists(deck_id);

-- Add foreign key constraint for list_id if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name='deck_cards' 
        AND constraint_type='FOREIGN KEY'
        AND constraint_name LIKE '%list_id%'
    ) THEN
        ALTER TABLE deck_cards 
        ADD CONSTRAINT fk_deck_cards_list_id 
        FOREIGN KEY (list_id) REFERENCES deck_custom_lists(id) ON DELETE SET NULL;
        RAISE NOTICE 'Added foreign key constraint for list_id';
    ELSE
        RAISE NOTICE 'Foreign key constraint already exists';
    END IF;
END $$;

