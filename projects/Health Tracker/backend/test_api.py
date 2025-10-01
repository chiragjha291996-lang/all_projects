#!/usr/bin/env python3
"""
Test script for Health Tracker API
"""

import requests
import json
from datetime import date, datetime

# API base URL
BASE_URL = "http://localhost:5002/api"

def test_api():
    print("Testing Health Tracker API...")
    print("=" * 50)
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running.")
        return
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return
    
    # Test data
    test_date = date.today().isoformat()
    test_data = {
        "mood": "Great",
        "energy": "High",
        "waterIntake": "<2L",
        "didRun": True,
        "distance": 5.5,
        "medications": ["thyroid", "b12"]
    }
    
    # Test saving data
    print(f"\n2. Testing save data for {test_date}...")
    try:
        response = requests.post(f"{BASE_URL}/health-data/{test_date}", json=test_data)
        if response.status_code == 200:
            print("✓ Data saved successfully")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Save failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Save error: {e}")
    
    # Test getting data
    print(f"\n3. Testing get data for {test_date}...")
    try:
        response = requests.get(f"{BASE_URL}/health-data/{test_date}")
        if response.status_code == 200:
            print("✓ Data retrieved successfully")
            data = response.json()
            print(f"  Mood: {data.get('mood')}")
            print(f"  Energy: {data.get('energy_level')}")
            print(f"  Water: {data.get('water_intake')}")
            print(f"  Did run: {data.get('did_run')}")
            print(f"  Distance: {data.get('distance_km')} km")
            print(f"  Medications: {data.get('medications')}")
        else:
            print(f"✗ Get failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Get error: {e}")
    
    # Test monthly data
    print(f"\n4. Testing monthly data...")
    try:
        current_date = date.today()
        response = requests.get(f"{BASE_URL}/health-data/monthly/{current_date.year}/{current_date.month}")
        if response.status_code == 200:
            print("✓ Monthly data retrieved successfully")
            data = response.json()
            print(f"  Found {len(data.get('data', []))} entries for {current_date.month}/{current_date.year}")
        else:
            print(f"✗ Monthly data failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Monthly data error: {e}")
    
    # Test dates with data
    print(f"\n5. Testing dates with data...")
    try:
        response = requests.get(f"{BASE_URL}/health-data/dates-with-data")
        if response.status_code == 200:
            print("✓ Dates with data retrieved successfully")
            data = response.json()
            print(f"  Found {len(data.get('dates', []))} dates with data")
            print(f"  Dates: {data.get('dates', [])}")
        else:
            print(f"✗ Dates with data failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Dates with data error: {e}")
    
    print("\n" + "=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_api()
