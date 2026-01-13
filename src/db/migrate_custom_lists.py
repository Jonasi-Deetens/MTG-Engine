# src/db/migrate_custom_lists.py

"""
Migration script to add custom lists functionality.
Adds list_id column to deck_cards and creates deck_custom_lists table.
"""

from sqlalchemy import text
from db.connection import engine

def migrate():
    """Run migration to add custom lists support."""
    print("Running migration for custom lists...")
    
    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()
        
        try:
            # Check if list_id column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='deck_cards' AND column_name='list_id'
            """))
            
            if result.fetchone() is None:
                print("Adding list_id column to deck_cards table...")
                conn.execute(text("""
                    ALTER TABLE deck_cards 
                    ADD COLUMN list_id INTEGER
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_deck_cards_list_id 
                    ON deck_cards(list_id)
                """))
                print("✓ Added list_id column")
            else:
                print("✓ list_id column already exists")
            
            # Check if deck_custom_lists table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='deck_custom_lists'
            """))
            
            if result.fetchone() is None:
                print("Creating deck_custom_lists table...")
                conn.execute(text("""
                    CREATE TABLE deck_custom_lists (
                        id SERIAL PRIMARY KEY,
                        deck_id INTEGER NOT NULL,
                        name VARCHAR NOT NULL,
                        position INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
                    )
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_deck_custom_lists_deck_id 
                    ON deck_custom_lists(deck_id)
                """))
                print("✓ Created deck_custom_lists table")
            else:
                print("✓ deck_custom_lists table already exists")
            
            # Add foreign key constraint for list_id if it doesn't exist
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name='deck_cards' 
                AND constraint_type='FOREIGN KEY'
                AND constraint_name LIKE '%list_id%'
            """))
            
            if result.fetchone() is None:
                print("Adding foreign key constraint for list_id...")
                conn.execute(text("""
                    ALTER TABLE deck_cards 
                    ADD CONSTRAINT fk_deck_cards_list_id 
                    FOREIGN KEY (list_id) REFERENCES deck_custom_lists(id) ON DELETE SET NULL
                """))
                print("✓ Added foreign key constraint")
            else:
                print("✓ Foreign key constraint already exists")
            
            trans.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"\n✗ Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate()

