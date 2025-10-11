#!/usr/bin/env python3
"""
Database Migration Script
Adds new prediction columns to existing equipment table
"""

import sqlite3

def migrate_database():
    """Add new prediction columns to equipment table"""
    conn = sqlite3.connect('predictive_maintenance.db')
    cursor = conn.cursor()
    
    try:
        # Add new columns to equipment table
        cursor.execute('ALTER TABLE equipment ADD COLUMN failure_prediction TEXT DEFAULT "No failure predicted"')
        cursor.execute('ALTER TABLE equipment ADD COLUMN prediction_confidence TEXT DEFAULT "Low"')
        cursor.execute('ALTER TABLE equipment ADD COLUMN prediction_urgency TEXT DEFAULT "SAFE"')
        
        print("✅ Successfully added new prediction columns to equipment table")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ Columns already exist, skipping migration")
        else:
            print(f"❌ Error adding columns: {e}")
            raise
    
    conn.commit()
    conn.close()
    
    print("🎉 Database migration completed!")

if __name__ == "__main__":
    migrate_database()
