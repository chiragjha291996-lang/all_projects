import sqlite3
import random
import time
import threading
from datetime import datetime, timedelta
import numpy as np

class IoTSimulator:
    def __init__(self, db_path='predictive_maintenance.db'):
        self.db_path = db_path
        self.running = False
        self.simulator_thread = None
        
        # Equipment configurations
        self.equipment_configs = {
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
        
        # Degradation patterns for realistic failure simulation
        self.degradation_factors = {1: 1.0, 2: 1.0, 3: 1.0}
        
    def get_db_connection(self):
        return sqlite3.connect(self.db_path)
    
    def generate_realistic_sensor_data(self, equipment_id, sensor_type):
        """Generate realistic sensor data with gradual degradation"""
        config = self.equipment_configs[equipment_id]['sensors'][sensor_type]
        degradation = self.degradation_factors[equipment_id]
        
        # Base value with some randomness
        base_min = config['min'] * degradation
        base_max = config['max'] * degradation
        
        # Add some realistic patterns
        if sensor_type == 'temperature':
            # Temperature gradually increases with degradation
            value = base_min + (base_max - base_min) * 0.3 + random.uniform(-5, 5)
        elif sensor_type == 'vibration':
            # Vibration increases with equipment wear
            value = base_min + (base_max - base_min) * 0.2 + random.uniform(-0.5, 0.5)
        elif sensor_type == 'pressure':
            # Pressure varies more randomly
            value = base_min + (base_max - base_min) * 0.4 + random.uniform(-3, 3)
        else:  # rpm
            # RPM decreases slightly with degradation
            value = base_max - (base_max - base_min) * 0.1 + random.uniform(-50, 50)
        
        # Ensure value stays within bounds
        value = max(config['min'], min(config['max'], value))
        
        return round(value, 2)
    
    def calculate_health_score(self, equipment_id):
        """Calculate health score based on sensor readings"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Get latest sensor readings
        cursor.execute('''
            SELECT sensor_type, value, threshold_max
            FROM sensor_data 
            WHERE equipment_id = ? 
            AND timestamp > datetime('now', '-5 minutes')
            ORDER BY timestamp DESC
        ''', (equipment_id,))
        
        readings = cursor.fetchall()
        conn.close()
        
        if not readings:
            return 100.0
        
        # Group by sensor type and get latest value
        sensor_values = {}
        for sensor_type, value, threshold in readings:
            if sensor_type not in sensor_values:
                sensor_values[sensor_type] = (value, threshold)
        
        # Calculate health score based on how close values are to thresholds
        total_score = 0
        sensor_count = 0
        
        for sensor_type, (value, threshold) in sensor_values.items():
            # Calculate percentage of threshold used
            threshold_usage = (value / threshold) * 100 if threshold > 0 else 0
            # Health score decreases as we approach threshold
            sensor_health = max(0, 100 - threshold_usage)
            total_score += sensor_health
            sensor_count += 1
        
        return round(total_score / sensor_count, 1) if sensor_count > 0 else 100.0
    
    def calculate_failure_probability(self, equipment_id, health_score):
        """Calculate failure probability based on health score"""
        # Simple inverse relationship: lower health = higher failure probability
        if health_score >= 80:
            return round(random.uniform(0, 20), 1)
        elif health_score >= 60:
            return round(random.uniform(20, 50), 1)
        elif health_score >= 40:
            return round(random.uniform(50, 80), 1)
        else:
            return round(random.uniform(80, 95), 1)
    
    def update_equipment_status(self, equipment_id, health_score, failure_probability):
        """Update equipment status based on health metrics"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Determine status based on health score
        if health_score >= 80:
            status = 'healthy'
        elif health_score >= 60:
            status = 'warning'
        else:
            status = 'critical'
        
        # Update equipment record
        cursor.execute('''
            UPDATE equipment 
            SET health_score = ?, failure_probability = ?, status = ?
            WHERE id = ?
        ''', (health_score, failure_probability, status, equipment_id))
        
        conn.commit()
        conn.close()
        
        return status
    
    def check_and_create_alerts(self, equipment_id, failure_probability, health_score):
        """Check if alerts should be created based on thresholds"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Check if we should create an alert
        should_alert = False
        severity = 'info'
        
        if failure_probability >= 80:
            severity = 'critical'
            should_alert = True
        elif failure_probability >= 60:
            severity = 'warning'
            should_alert = True
        elif health_score < 50:
            severity = 'warning'
            should_alert = True
        
        if should_alert:
            # Check if there's already an active alert for this equipment
            cursor.execute('''
                SELECT COUNT(*) FROM alerts 
                WHERE equipment_id = ? AND status = 'active'
            ''', (equipment_id,))
            
            if cursor.fetchone()[0] == 0:
                # Create new alert
                cursor.execute('''
                    INSERT INTO alerts (equipment_id, severity, failure_probability, sensor_trigger, status)
                    VALUES (?, ?, ?, ?, 'active')
                ''', (equipment_id, severity, failure_probability, 'health_threshold'))
        
        conn.commit()
        conn.close()
    
    def simulate_data_generation(self):
        """Main simulation loop"""
        while self.running:
            try:
                for equipment_id in self.equipment_configs.keys():
                    conn = self.get_db_connection()
                    cursor = conn.cursor()
                    
                    try:
                        # Generate sensor data
                        for sensor_type, config in self.equipment_configs[equipment_id]['sensors'].items():
                            value = self.generate_realistic_sensor_data(equipment_id, sensor_type)
                            
                            # Insert sensor data
                            cursor.execute('''
                                INSERT INTO sensor_data (equipment_id, sensor_type, value, threshold_min, threshold_max)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (equipment_id, sensor_type, value, config['min'], config['max']))
                        
                        conn.commit()
                        conn.close()
                        
                        # Calculate health metrics (separate connection)
                        health_score = self.calculate_health_score(equipment_id)
                        failure_probability = self.calculate_failure_probability(equipment_id, health_score)
                        
                        # Update equipment status (separate connection)
                        status = self.update_equipment_status(equipment_id, health_score, failure_probability)
                        
                        # Check for alerts (separate connection)
                        self.check_and_create_alerts(equipment_id, failure_probability, health_score)
                        
                        # Gradually increase degradation for realistic failure simulation
                        if random.random() < 0.1:  # 10% chance to increase degradation
                            self.degradation_factors[equipment_id] = min(1.5, self.degradation_factors[equipment_id] + 0.01)
                    
                    except Exception as e:
                        print(f"Error processing equipment {equipment_id}: {e}")
                        conn.close()
                        continue
                
                # Wait 1 second before next data generation
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in simulation: {e}")
                time.sleep(1)
    
    def start(self):
        """Start the IoT simulator"""
        if not self.running:
            self.running = True
            self.simulator_thread = threading.Thread(target=self.simulate_data_generation)
            self.simulator_thread.daemon = True
            self.simulator_thread.start()
            print("IoT Simulator started")
    
    def stop(self):
        """Stop the IoT simulator"""
        self.running = False
        if self.simulator_thread:
            self.simulator_thread.join()
        print("IoT Simulator stopped")

# Global simulator instance
simulator = IoTSimulator()
