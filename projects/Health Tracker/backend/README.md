# Health Tracker Database Schema

## Overview
This database is designed to store health tracking data for a personal health monitoring application. The schema is optimized for both daily data entry and future analytics capabilities.

## Database Structure

### Tables

#### 1. `daily_entries` (Main table)
- **id**: Primary key (auto-increment)
- **date**: Date in YYYY-MM-DD format (unique)
- **mood**: Text field for mood description
- **energy_level**: Text field for energy level description
- **water_intake**: Text field for water consumption (<1L, <2L, <3L)
- **created_at**: Timestamp when record was created
- **updated_at**: Timestamp when record was last updated

#### 2. `running_activities`
- **id**: Primary key (auto-increment)
- **date**: Date (foreign key to daily_entries.date)
- **did_run**: Boolean (0/1) - whether user ran that day
- **distance_km**: Real number - distance in kilometers (only if did_run = 1)
- **created_at**: Timestamp when record was created
- **updated_at**: Timestamp when record was last updated

#### 3. `medication_tracking`
- **id**: Primary key (auto-increment)
- **date**: Date (foreign key to daily_entries.date)
- **thyroid**: Boolean (0/1) - thyroid medication taken
- **b12**: Boolean (0/1) - B12 medication taken
- **finasteride**: Boolean (0/1) - finasteride medication taken
- **created_at**: Timestamp when record was created
- **updated_at**: Timestamp when record was last updated

## Key Features

### Data Integrity
- Foreign key relationships ensure data consistency
- Unique constraints prevent duplicate daily entries
- Proper indexing for optimal query performance

### Analytics-Ready Design
- Normalized structure allows for complex queries
- Date-based indexing enables efficient time-series analysis
- Separate tables for different data types allow for focused analytics

### Future Analytics Capabilities
The schema supports various analytics queries:
- Monthly/weekly trends for mood, energy, and water intake
- Running performance tracking over time
- Medication adherence monitoring
- Correlation analysis between different health metrics
- Custom date range reporting

## Usage

### Initialize Database
```python
from database import HealthTrackerDB
db = HealthTrackerDB()
```

### Save Daily Entry
```python
db.save_daily_entry(
    date="2025-09-13",
    mood="Good",
    energy_level="High",
    water_intake="<2L"
)
```

### Save Running Data
```python
db.save_running_data(
    date="2025-09-13",
    did_run=True,
    distance_km=5.5
)
```

### Save Medication Data
```python
db.save_medication_data(
    date="2025-09-13",
    thyroid=True,
    b12=True,
    finasteride=False
)
```

### Retrieve Data
```python
# Get complete daily entry
entry = db.get_daily_entry("2025-09-13")

# Get monthly data for analytics
monthly_data = db.get_monthly_data(2025, 9)
```

## Database File
- **File**: `health_tracker.db` (SQLite)
- **Location**: Backend directory
- **Backup**: Consider regular backups for data safety
