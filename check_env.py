import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

print("Environment Variables:")
print(f"DATABASE_URL = {os.environ.get('DATABASE_URL', 'Not set')}")
print(f"FLASK_ENV = {os.environ.get('FLASK_ENV', 'Not set')}")
print(f"FLASK_DEBUG = {os.environ.get('FLASK_DEBUG', 'Not set')}")

# Check database files
dent_track_db = "instance/dent_track.db"
denttrack_db = "instance/denttrack.db"

print("\nDatabase Files:")
print(f"{dent_track_db} exists: {os.path.exists(dent_track_db)}")
print(f"{denttrack_db} exists: {os.path.exists(denttrack_db)}")

# Try to connect to dent_track.db and list tables
if os.path.exists(dent_track_db):
    try:
        conn = sqlite3.connect(dent_track_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in {dent_track_db}:")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"Error connecting to {dent_track_db}: {e}")

# Try to connect to denttrack.db and list tables
if os.path.exists(denttrack_db):
    try:
        conn = sqlite3.connect(denttrack_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in {denttrack_db}:")
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"Error connecting to {denttrack_db}: {e}") 