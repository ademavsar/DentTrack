#!/usr/bin/env python
"""
Database Path Migration Script

This script ensures that the database path is standardized to use 'denttrack.db'
instead of 'dent_track.db'. It handles the migration of database files and updates
any necessary configuration.

Usage:
    python db_migrate_path.py
"""

import os
import shutil
import sys
import sqlite3
from dotenv import load_dotenv, set_key

# Constants
LEGACY_DB_PATH = "instance/dent_track.db"
STANDARD_DB_PATH = "instance/denttrack.db"
ENV_FILE = ".env"

def main():
    """
    Main migration function that coordinates the database path standardization.
    """
    print("\n===================================================")
    print(" DentTrack Database Path Standardization Tool")
    print("===================================================")
    
    # Step 1: Load environment variables
    load_dotenv()
    current_db_url = os.environ.get('DATABASE_URL', '')
    
    print(f"\nCurrent DATABASE_URL: {current_db_url}")
    
    # Step 2: Check for database files
    legacy_exists = os.path.exists(LEGACY_DB_PATH)
    standard_exists = os.path.exists(STANDARD_DB_PATH)
    
    print(f"\nDatabase file status:")
    print(f"  - Legacy path ({LEGACY_DB_PATH}): {'EXISTS' if legacy_exists else 'NOT FOUND'}")
    print(f"  - Standard path ({STANDARD_DB_PATH}): {'EXISTS' if standard_exists else 'NOT FOUND'}")
    
    # Step 3: Handle migration based on file existence
    if not legacy_exists and not standard_exists:
        print("\nNo database files found. No migration needed.")
        print("A new database will be created at the standard path when the application runs.")
        ensure_env_variable_standardized()
        return
    
    if legacy_exists and not standard_exists:
        print(f"\nMigrating database from legacy path to standard path:")
        print(f"  {LEGACY_DB_PATH} -> {STANDARD_DB_PATH}")
        
        # Create instance directory if it doesn't exist
        os.makedirs(os.path.dirname(STANDARD_DB_PATH), exist_ok=True)
        
        # Copy the database
        try:
            shutil.copy2(LEGACY_DB_PATH, STANDARD_DB_PATH)
            print("✓ Database copied successfully")
            
            # Verify the new database
            if verify_database(STANDARD_DB_PATH):
                print("✓ Database verification successful")
                print(f"\nWould you like to remove the legacy database file? (y/n)")
                choice = input().lower()
                if choice == 'y':
                    try:
                        os.remove(LEGACY_DB_PATH)
                        print(f"✓ Legacy database file removed: {LEGACY_DB_PATH}")
                    except Exception as e:
                        print(f"! Error removing legacy database: {e}")
                else:
                    print("Legacy database file kept for reference.")
            else:
                print("! Database verification failed")
                print("Please check the database files manually.")
                sys.exit(1)
        except Exception as e:
            print(f"! Error during database migration: {e}")
            sys.exit(1)
    
    if legacy_exists and standard_exists:
        print("\nBoth legacy and standard database files exist.")
        
        # Check if they are identical
        if are_files_identical(LEGACY_DB_PATH, STANDARD_DB_PATH):
            print("The files are identical. The legacy file can be removed.")
            print(f"\nWould you like to remove the legacy database file? (y/n)")
            choice = input().lower()
            if choice == 'y':
                try:
                    os.remove(LEGACY_DB_PATH)
                    print(f"✓ Legacy database file removed: {LEGACY_DB_PATH}")
                except Exception as e:
                    print(f"! Error removing legacy database: {e}")
        else:
            # Compare database structures
            print("\nCOMPARING DATABASE STRUCTURES:")
            print_database_info(LEGACY_DB_PATH, "Legacy")
            print_database_info(STANDARD_DB_PATH, "Standard")
            
            print("\nThe files have different content. Please choose how to proceed:")
            print("1. Keep both files (no action)")
            print("2. Use legacy file (overwrite standard file)")
            print("3. Use standard file (delete legacy file)")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '2':
                try:
                    shutil.copy2(LEGACY_DB_PATH, STANDARD_DB_PATH)
                    print(f"✓ Standard database overwritten with legacy database")
                    
                    # Ask if they want to remove the legacy file
                    print(f"\nWould you like to remove the legacy database file? (y/n)")
                    remove_choice = input().lower()
                    if remove_choice == 'y':
                        os.remove(LEGACY_DB_PATH)
                        print(f"✓ Legacy database file removed: {LEGACY_DB_PATH}")
                except Exception as e:
                    print(f"! Error: {e}")
            elif choice == '3':
                try:
                    os.remove(LEGACY_DB_PATH)
                    print(f"✓ Legacy database file removed: {LEGACY_DB_PATH}")
                except Exception as e:
                    print(f"! Error removing legacy database: {e}")
    
    # Step 4: Update the DATABASE_URL in .env if needed
    ensure_env_variable_standardized()
    
    print("\n===================================================")
    print(" Database Path Standardization Complete")
    print("===================================================")
    print("\nThe application will now use the standardized database path:")
    print(f"  {STANDARD_DB_PATH}")
    print("\nPlease restart any running instances of the application.")

def verify_database(db_path):
    """Verify that the database file exists and can be opened."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        return len(tables) > 0
    except Exception as e:
        print(f"Database verification error: {e}")
        return False

def are_files_identical(file1, file2):
    """Check if two files have identical content."""
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() == f2.read()
    except Exception as e:
        print(f"Error comparing files: {e}")
        return False

def print_database_info(db_path, label):
    """Print information about the database tables."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n{label} database ({db_path}):")
        if len(tables) == 0:
            print("  No tables found")
        else:
            print(f"  Contains {len(tables)} tables:")
            for table in tables:
                # Get row count
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"    - {table[0]} ({count} rows)")
                except:
                    print(f"    - {table[0]} (error getting row count)")
        
        conn.close()
    except Exception as e:
        print(f"Error analyzing database {db_path}: {e}")

def ensure_env_variable_standardized():
    """Update the DATABASE_URL in .env to use the standardized path."""
    if not os.path.exists(ENV_FILE):
        print(f"\n.env file not found at {ENV_FILE}. Creating a new one.")
        with open(ENV_FILE, 'w') as f:
            f.write(f"DATABASE_URL=sqlite:///{STANDARD_DB_PATH}\n")
        print("✓ Created .env file with standardized DATABASE_URL")
        return
    
    # Load current environment
    load_dotenv()
    current_db_url = os.environ.get('DATABASE_URL', '')
    
    # Check if DATABASE_URL needs to be updated
    if 'dent_track.db' in current_db_url:
        # Load the entire .env file
        with open(ENV_FILE, 'r') as f:
            env_content = f.read()
        
        # Replace the DATABASE_URL
        new_db_url = current_db_url.replace('dent_track.db', 'denttrack.db')
        env_content = env_content.replace(current_db_url, new_db_url)
        
        # Write back the file
        with open(ENV_FILE, 'w') as f:
            f.write(env_content)
        
        print(f"✓ Updated DATABASE_URL in .env file:")
        print(f"  FROM: {current_db_url}")
        print(f"  TO:   {new_db_url}")
    else:
        print(f"✓ DATABASE_URL is already standardized in .env file")

if __name__ == "__main__":
    main() 