import sqlite3
import os
from datetime import datetime, date

class HealthTrackerDB:
    def __init__(self, db_path="health_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create daily_entries table - main table for daily health data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                mood TEXT,
                energy_level TEXT,
                water_intake TEXT,
                sleep_time TEXT,
                wake_time TEXT,
                left_bed_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create running_activities table - for running data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS running_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                did_run BOOLEAN NOT NULL DEFAULT 0,
                distance_km REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (date) REFERENCES daily_entries(date)
            )
        ''')
        
        # Create medication_tracking table - for medication data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medication_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                thyroid BOOLEAN NOT NULL DEFAULT 0,
                b12 BOOLEAN NOT NULL DEFAULT 0,
                finasteride BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (date) REFERENCES daily_entries(date)
            )
        ''')
        
        # Add sleep columns to existing tables (migration)
        try:
            cursor.execute('ALTER TABLE daily_entries ADD COLUMN sleep_time TEXT')
        except:
            pass  # Column already exists
        try:
            cursor.execute('ALTER TABLE daily_entries ADD COLUMN wake_time TEXT')
        except:
            pass  # Column already exists
        try:
            cursor.execute('ALTER TABLE daily_entries ADD COLUMN left_bed_time TEXT')
        except:
            pass  # Column already exists
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_entries_date ON daily_entries(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_running_activities_date ON running_activities(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_medication_tracking_date ON medication_tracking(date)')
        
        conn.commit()
        conn.close()
    
    def get_daily_entry(self, target_date):
        """Get complete daily entry for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get main daily entry
        cursor.execute('SELECT * FROM daily_entries WHERE date = ?', (target_date,))
        daily_entry = cursor.fetchone()
        
        # Get running data
        cursor.execute('SELECT * FROM running_activities WHERE date = ?', (target_date,))
        running_data = cursor.fetchone()
        
        # Get medication data
        cursor.execute('SELECT * FROM medication_tracking WHERE date = ?', (target_date,))
        medication_data = cursor.fetchone()
        
        conn.close()
        
        return {
            'daily_entry': daily_entry,
            'running_data': running_data,
            'medication_data': medication_data
        }
    
    def save_daily_entry(self, date, mood=None, energy_level=None, water_intake=None, sleep_time=None, wake_time=None, left_bed_time=None):
        """Save or update daily entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_entries (date, mood, energy_level, water_intake, sleep_time, wake_time, left_bed_time, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (date, mood, energy_level, water_intake, sleep_time, wake_time, left_bed_time))
        
        conn.commit()
        conn.close()
    
    def save_running_data(self, date, did_run, distance_km=None):
        """Save or update running data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO running_activities (date, did_run, distance_km, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (date, did_run, distance_km))
        
        conn.commit()
        conn.close()
    
    def save_medication_data(self, date, thyroid=False, b12=False, finasteride=False):
        """Save or update medication data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO medication_tracking (date, thyroid, b12, finasteride, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (date, thyroid, b12, finasteride))
        
        conn.commit()
        conn.close()
    
    def get_monthly_data(self, year, month):
        """Get all data for a specific month (for analytics)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all daily entries for the month
        cursor.execute('''
            SELECT de.*, ra.did_run, ra.distance_km, 
                   mt.thyroid, mt.b12, mt.finasteride
            FROM daily_entries de
            LEFT JOIN running_activities ra ON de.date = ra.date
            LEFT JOIN medication_tracking mt ON de.date = mt.date
            WHERE strftime('%Y', de.date) = ? AND strftime('%m', de.date) = ?
            ORDER BY de.date
        ''', (str(year), str(month).zfill(2)))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_date_range_data(self, start_date, end_date):
        """Get data for a date range (for analytics)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT de.*, ra.did_run, ra.distance_km, 
                   mt.thyroid, mt.b12, mt.finasteride
            FROM daily_entries de
            LEFT JOIN running_activities ra ON de.date = ra.date
            LEFT JOIN medication_tracking mt ON de.date = mt.date
            WHERE de.date BETWEEN ? AND ?
            ORDER BY de.date
        ''', (start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def delete_daily_entry(self, target_date):
        """Delete all health data for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete from all related tables
            cursor.execute('DELETE FROM running_activities WHERE date = ?', (target_date,))
            cursor.execute('DELETE FROM medication_tracking WHERE date = ?', (target_date,))
            cursor.execute('DELETE FROM daily_entries WHERE date = ?', (target_date,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_dates_with_data(self, start_date, end_date):
        """Get all dates that have health data in a range"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT date 
            FROM daily_entries 
            WHERE date BETWEEN ? AND ?
            ORDER BY date
        ''', (start_date, end_date))
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results

if __name__ == "__main__":
    # Initialize database
    db = HealthTrackerDB()
    print("Database initialized successfully!")
    print("Tables created:")
    print("- daily_entries: mood, energy_level, water_intake")
    print("- running_activities: did_run, distance_km")
    print("- medication_tracking: thyroid, b12, finasteride")
    print("\nDatabase is ready for the health tracking app!")
