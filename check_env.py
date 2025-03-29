import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

print("Environment Variables:")
print(f"DATABASE_URL = {os.environ.get('DATABASE_URL', 'Not set')}")
print(f"FLASK_ENV = {os.environ.get('FLASK_ENV', 'Not set')}")
print(f"FLASK_DEBUG = {os.environ.get('FLASK_DEBUG', 'Not set')}")

# Check database files
# Note: Only checking for standardized denttrack.db (legacy dent_track.db included for information only)
denttrack_db = "instance/denttrack.db"
legacy_db = "instance/dent_track.db"

print("\nDatabase Files:")
print(f"{denttrack_db} exists: {os.path.exists(denttrack_db)} (STANDARD PATH)")
print(f"{legacy_db} exists: {os.path.exists(legacy_db)} (LEGACY PATH - will be deprecated)")

# Try to connect to the standardized database
if os.path.exists(denttrack_db):
    try:
        conn = sqlite3.connect(denttrack_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in {denttrack_db} (STANDARD PATH):")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"Error connecting to {denttrack_db}: {e}")

# Try to connect to the legacy database (for information only)
if os.path.exists(legacy_db) and legacy_db != denttrack_db:
    try:
        conn = sqlite3.connect(legacy_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in {legacy_db} (LEGACY PATH - FOR REFERENCE ONLY):")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"Error connecting to {legacy_db}: {e}") 