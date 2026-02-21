import sqlite3
import os

# Define database path
db_path = "hr_system.db"

# SQL commands from migration_snapshot.sql
sql_commands = [
    "ALTER TABLE interview_sessions ADD COLUMN candidate_name VARCHAR;",
    "ALTER TABLE interview_sessions ADD COLUMN candidate_phone VARCHAR;",
    "ALTER TABLE interview_sessions ADD COLUMN candidate_email VARCHAR;",
    """
    UPDATE interview_sessions
    SET 
        candidate_name = (SELECT name FROM candidates WHERE candidates.id = interview_sessions.candidate_id),
        candidate_phone = (SELECT phone FROM candidates WHERE candidates.id = interview_sessions.candidate_id),
        candidate_email = (SELECT email FROM candidates WHERE candidates.id = interview_sessions.candidate_id);
    """
]

def apply_migration():
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for sql in sql_commands:
        try:
            print(f"Executing: {sql[:50]}...")
            cursor.execute(sql)
            print("Success.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Skipping (already exists): {e}")
            else:
                print(f"Error executing SQL: {e}")
    
    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    apply_migration()
