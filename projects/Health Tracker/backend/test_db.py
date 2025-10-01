#!/usr/bin/env python3
"""
Test script to verify database schema and functionality
"""

from database import HealthTrackerDB
from datetime import date, datetime

def test_database():
    print("Testing Health Tracker Database...")
    print("=" * 50)
    
    # Initialize database
    db = HealthTrackerDB()
    print("✓ Database initialized")
    
    # Test saving sample data
    today = date.today().isoformat()
    
    # Save daily entry
    db.save_daily_entry(
        date=today,
        mood="Good",
        energy_level="High",
        water_intake="<2L"
    )
    print("✓ Daily entry saved")
    
    # Save running data
    db.save_running_data(
        date=today,
        did_run=True,
        distance_km=5.5
    )
    print("✓ Running data saved")
    
    # Save medication data
    db.save_medication_data(
        date=today,
        thyroid=True,
        b12=True,
        finasteride=False
    )
    print("✓ Medication data saved")
    
    # Test retrieving data
    entry_data = db.get_daily_entry(today)
    print("\nRetrieved data for today:")
    print(f"Daily Entry: {entry_data['daily_entry']}")
    print(f"Running Data: {entry_data['running_data']}")
    print(f"Medication Data: {entry_data['medication_data']}")
    
    # Test monthly data retrieval
    current_year = datetime.now().year
    current_month = datetime.now().month
    monthly_data = db.get_monthly_data(current_year, current_month)
    print(f"\nMonthly data for {current_month}/{current_year}: {len(monthly_data)} entries")
    
    print("\n" + "=" * 50)
    print("✓ All database tests passed!")
    print("Database schema is ready for the health tracking app.")

if __name__ == "__main__":
    test_database()
