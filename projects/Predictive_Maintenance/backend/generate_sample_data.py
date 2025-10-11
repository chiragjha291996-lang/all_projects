#!/usr/bin/env python3
"""
Generate sample sensor data for testing the Equipment Detail page
"""

import sqlite3
import random
import time
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample sensor data for all equipment"""
    conn = sqlite3.connect('predictive_maintenance.db')
    cursor = conn.cursor()
    
    # Equipment configurations
    equipment_configs = {
        1: {  # Pump
            'name': 'Pump-001',
            'sensors': {
                'temperature': {'min': 20, 'max': 80, 'threshold': 70},
                'vibration': {'min': 0.1, 'max': 5.0, 'threshold': 4.0},
                'pressure': {'min': 10, 'max': 50, 'threshold': 45},
                'rpm': {'min': 1000, 'max': 3000, 'threshold': 2800}
            }
        },
        2: {  # Compressor
            'name': 'Compressor-002',
            'sensors': {
                'temperature': {'min': 15, 'max': 90, 'threshold': 80},
                'vibration': {'min': 0.2, 'max': 6.0, 'threshold': 5.0},
                'pressure': {'min': 5, 'max': 60, 'threshold': 55},
                'rpm': {'min': 800, 'max': 2500, 'threshold': 2300}
            }
        },
        3: {  # Conveyor Belt
            'name': 'Conveyor-003',
            'sensors': {
                'temperature': {'min': 10, 'max': 60, 'threshold': 50},
                'vibration': {'min': 0.05, 'max': 3.0, 'threshold': 2.5},
                'pressure': {'min': 0, 'max': 20, 'threshold': 18},
                'rpm': {'min': 500, 'max': 1500, 'threshold': 1400}
            }
        }
    }
    
    # Generate data for the last hour (every 5 minutes = 12 data points)
    base_time = datetime.now() - timedelta(hours=1)
    
    for equipment_id, config in equipment_configs.items():
        print(f"Generating data for {config['name']}...")
        
        for i in range(12):  # 12 data points over 1 hour
            timestamp = base_time + timedelta(minutes=i*5)
            
            for sensor_type, sensor_config in config['sensors'].items():
                # Generate realistic value with some variation
                base_value = sensor_config['min'] + (sensor_config['max'] - sensor_config['min']) * 0.3
                variation = random.uniform(-0.2, 0.2) * (sensor_config['max'] - sensor_config['min'])
                value = max(sensor_config['min'], min(sensor_config['max'], base_value + variation))
                
                cursor.execute('''
                    INSERT INTO sensor_data (equipment_id, sensor_type, value, threshold_min, threshold_max, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (equipment_id, sensor_type, round(value, 2), sensor_config['min'], sensor_config['max'], timestamp))
    
    conn.commit()
    conn.close()
    print("Sample data generated successfully!")

if __name__ == "__main__":
    generate_sample_data()
