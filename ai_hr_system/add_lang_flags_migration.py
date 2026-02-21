"""
Database Migration: Add candidate_lang and flags to interview_sessions table

This migration adds two new columns:
1. candidate_lang - stores the language used during the interview session
2. flags - stores AI analysis flags as JSON

Run this script to update the database schema.
"""

from app.database import engine
from sqlalchemy import text, inspect

def run_migration():
    """Add candidate_lang and flags columns to interview_sessions table"""
    try:
        print("Starting migration: Adding candidate_lang and flags columns...")
        
        # Check if columns already exist
        inspector = inspect(engine)
        columns = inspector.get_columns('interview_sessions')
        existing_columns = [col['name'] for col in columns]
        
        # Add candidate_lang if it doesn't exist
        if 'candidate_lang' not in existing_columns:
            print("Adding candidate_lang column...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE interview_sessions ADD COLUMN candidate_lang VARCHAR DEFAULT 'en'"))
                conn.commit()
            print("✓ candidate_lang column added")
        else:
            print("✓ candidate_lang column already exists")
        
        # Add flags if it doesn't exist
        if 'flags' not in existing_columns:
            print("Adding flags column...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE interview_sessions ADD COLUMN flags JSON"))
                conn.commit()
            print("✓ flags column added")
        else:
            print("✓ flags column already exists")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
