"""
Enhanced IoT Simulator with Anomaly Injection
Generates realistic sensor data with various anomaly patterns for alert generation
"""

import sqlite3
import time
import random
import numpy as np
from datetime import datetime, timedelta
import threading
import json
from sensor_thresholds import SensorThresholds

class AnomalyInjector:
    def __init__(self):
        self.anomaly_patterns = {
            'temperature_spike': {
                'probability': 0.03,  # 3% chance per cycle (reduced from 15%)
                'magnitude': (20, 50),  # Temperature increase range
                'duration': (5, 15),  # Duration in cycles
                'description': 'Temperature spike anomaly'
            },
            'vibration_increase': {
                'probability': 0.025,  # 2.5% chance per cycle (reduced from 12%)
                'magnitude': (2, 8),  # Vibration increase range
                'duration': (8, 20),  # Duration in cycles
                'description': 'Vibration increase anomaly'
            },
            'pressure_drop': {
                'probability': 0.02,  # 2% chance per cycle (reduced from 10%)
                'magnitude': (5, 15),  # Pressure decrease range
                'duration': (6, 18),  # Duration in cycles
                'description': 'Pressure drop anomaly'
            },
            'rpm_fluctuation': {
                'probability': 0.015,  # 1.5% chance per cycle (reduced from 8%)
                'magnitude': (100, 300),  # RPM fluctuation range
                'duration': (10, 25),  # Duration in cycles
                'description': 'RPM fluctuation anomaly'
            },
            'gradual_degradation': {
                'probability': 0.01,  # 1% chance per cycle (reduced from 5%)
                'magnitude': (0.5, 2),  # Gradual increase per cycle
                'duration': (30, 60),  # Duration in cycles
                'description': 'Gradual degradation anomaly'
            },
            'sudden_failure': {
                'probability': 0.005,  # 0.5% chance per cycle (reduced from 2%)
                'magnitude': (50, 100),  # Sudden increase
                'duration': (1, 3),  # Very short duration
                'description': 'Sudden failure anomaly'
            }
        }
        
        # Track active anomalies per equipment
        self.active_anomalies = {}
        
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect('predictive_maintenance.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def inject_anomaly(self, equipment_id, sensor_type, base_value, cycle_count):
        """Inject anomaly into sensor data"""
        if equipment_id not in self.active_anomalies:
            self.active_anomalies[equipment_id] = {}
        
        # Check for new anomalies
        for pattern_name, pattern_config in self.anomaly_patterns.items():
            if random.random() < pattern_config['probability']:
                if pattern_name not in self.active_anomalies[equipment_id]:
                    # Start new anomaly
                    duration = random.randint(pattern_config['duration'][0], pattern_config['duration'][1])
                    magnitude = random.uniform(pattern_config['magnitude'][0], pattern_config['magnitude'][1])
                    
                    self.active_anomalies[equipment_id][pattern_name] = {
                        'start_cycle': cycle_count,
                        'duration': duration,
                        'magnitude': magnitude,
                        'description': pattern_config['description'],
                        'sensor_type': sensor_type
                    }
        
        # Apply active anomalies
        anomaly_value = 0
        anomalies_to_remove = []
        
        for pattern_name, anomaly in self.active_anomalies[equipment_id].items():
            cycles_elapsed = cycle_count - anomaly['start_cycle']
            
            if cycles_elapsed < anomaly['duration']:
                # Apply anomaly based on pattern
                if pattern_name == 'temperature_spike' and sensor_type == 'temperature':
                    anomaly_value += anomaly['magnitude']
                elif pattern_name == 'vibration_increase' and sensor_type == 'vibration':
                    anomaly_value += anomaly['magnitude']
                elif pattern_name == 'pressure_drop' and sensor_type == 'pressure':
                    anomaly_value -= anomaly['magnitude']
                elif pattern_name == 'rpm_fluctuation' and sensor_type == 'rpm':
                    anomaly_value += random.uniform(-anomaly['magnitude'], anomaly['magnitude'])
                elif pattern_name == 'gradual_degradation':
                    anomaly_value += anomaly['magnitude'] * cycles_elapsed
                elif pattern_name == 'sudden_failure':
                    anomaly_value += anomaly['magnitude']
            else:
                # Anomaly expired
                anomalies_to_remove.append(pattern_name)
        
        # Remove expired anomalies
        for pattern_name in anomalies_to_remove:
            del self.active_anomalies[equipment_id][pattern_name]
        
        return anomaly_value
    
    def get_anomaly_status(self, equipment_id):
        """Get current anomaly status for equipment"""
        if equipment_id not in self.active_anomalies:
            return []
        
        return list(self.active_anomalies[equipment_id].values())

class EnhancedIoT_Simulator:
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        self.anomaly_injector = AnomalyInjector()
        
        # Equipment configurations with more realistic ranges
        self.equipment_configs = {
            1: {
                'name': 'Pump-001',
                'type': 'Centrifugal Pump',
                'base_temperature': 65.0,
                'base_vibration': 1.2,
                'base_pressure': 20.0,
                'base_rpm': 1800,
                'degradation_factor': 0.001
            },
            2: {
                'name': 'Compressor-002',
                'type': 'Air Compressor',
                'base_temperature': 75.0,
                'base_vibration': 1.8,
                'base_pressure': 25.0,
                'base_rpm': 2200,
                'degradation_factor': 0.0015
            },
            3: {
                'name': 'Motor-003',
                'type': 'Electric Motor',
                'base_temperature': 70.0,
                'base_vibration': 1.5,
                'base_pressure': 15.0,
                'base_rpm': 1500,
                'degradation_factor': 0.0008
            }
        }
    
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect('predictive_maintenance.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_realistic_sensor_data(self, equipment_id):
        """Generate realistic sensor data with anomalies"""
        config = self.equipment_configs[equipment_id]
        
        # Base values with gradual degradation
        degradation = self.cycle_count * config['degradation_factor']
        
        base_temperature = config['base_temperature'] + degradation
        base_vibration = config['base_vibration'] + degradation
        base_pressure = config['base_pressure'] - degradation * 0.5
        base_rpm = config['base_rpm'] + random.uniform(-50, 50)
        
        # Generate sensor data with anomalies
        sensors = {}
        
        # Temperature with anomaly injection
        temp_anomaly = self.anomaly_injector.inject_anomaly(equipment_id, 'temperature', base_temperature, self.cycle_count)
        sensors['temperature'] = base_temperature + temp_anomaly + random.uniform(-2, 2)
        
        # Vibration with anomaly injection
        vib_anomaly = self.anomaly_injector.inject_anomaly(equipment_id, 'vibration', base_vibration, self.cycle_count)
        sensors['vibration'] = base_vibration + vib_anomaly + random.uniform(-0.1, 0.1)
        
        # Pressure with anomaly injection
        press_anomaly = self.anomaly_injector.inject_anomaly(equipment_id, 'pressure', base_pressure, self.cycle_count)
        sensors['pressure'] = base_pressure + press_anomaly + random.uniform(-0.5, 0.5)
        
        # RPM with anomaly injection
        rpm_anomaly = self.anomaly_injector.inject_anomaly(equipment_id, 'rpm', base_rpm, self.cycle_count)
        sensors['rpm'] = base_rpm + rpm_anomaly + random.uniform(-25, 25)
        
        # Ensure realistic bounds
        sensors['temperature'] = max(20, min(120, sensors['temperature']))
        sensors['vibration'] = max(0.1, min(10, sensors['vibration']))
        sensors['pressure'] = max(5, min(50, sensors['pressure']))
        sensors['rpm'] = max(500, min(3000, sensors['rpm']))
        
        return sensors
    
    def calculate_health_score(self, sensors):
        """Calculate health score based on sensor data"""
        # Normalize sensor values to 0-100 scale
        temp_score = max(0, 100 - (sensors['temperature'] - 60) * 2)
        vib_score = max(0, 100 - (sensors['vibration'] - 1) * 20)
        press_score = max(0, 100 - abs(sensors['pressure'] - 20) * 3)
        rpm_score = max(0, 100 - abs(sensors['rpm'] - 1800) * 0.05)
        
        # Weighted average
        health_score = (temp_score * 0.3 + vib_score * 0.3 + press_score * 0.2 + rpm_score * 0.2)
        return max(0, min(100, health_score))
    
    def calculate_failure_probability(self, sensors, health_score):
        """Calculate failure probability based on sensor data and health score"""
        # Base failure probability from health score
        base_prob = (100 - health_score) / 100 * 30  # Max 30% from health
        
        # Additional factors
        temp_factor = max(0, (sensors['temperature'] - 80) * 2)  # High temp increases risk
        vib_factor = max(0, (sensors['vibration'] - 3) * 5)     # High vibration increases risk
        press_factor = max(0, abs(sensors['pressure'] - 20) * 1) # Pressure deviation increases risk
        
        failure_prob = base_prob + temp_factor + vib_factor + press_factor
        return max(0, min(100, failure_prob))
    
    def convert_to_time_prediction(self, failure_probability, health_score):
        """Convert failure probability to time-based prediction with confidence"""
        # Stabilize the probability to reduce constant changes
        stabilized_prob = round(failure_probability / 5) * 5  # Round to nearest 5%
        
        # Determine time range and confidence based on probability and health score
        if stabilized_prob >= 80 or health_score < 20:
            time_range = "2-4 hours"
            confidence = "High"
            urgency = "IMMEDIATE"
        elif stabilized_prob >= 60 or health_score < 40:
            time_range = "6-12 hours"
            confidence = "High"
            urgency = "URGENT"
        elif stabilized_prob >= 40 or health_score < 60:
            time_range = "1-2 days"
            confidence = "Medium"
            urgency = "SCHEDULE"
        elif stabilized_prob >= 20 or health_score < 80:
            time_range = "3-7 days"
            confidence = "Medium"
            urgency = "MONITOR"
        else:
            time_range = "7+ days"
            confidence = "Low"
            urgency = "SAFE"
        
        return {
            'time_range': time_range,
            'confidence': confidence,
            'urgency': urgency,
            'probability': stabilized_prob,
            'message': f"Failure predicted in {time_range}"
        }
    
    def update_equipment_status(self, equipment_id, health_score, failure_probability):
        """Update equipment status based on real-time sensor data with hysteresis"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Get current status to implement hysteresis
        cursor.execute('SELECT status FROM equipment WHERE id = ?', (equipment_id,))
        result = cursor.fetchone()
        current_status = result[0] if result else 'healthy'
        
        # Determine new status with hysteresis to prevent rapid changes
        if current_status == 'healthy':
            # Need lower threshold to change from healthy
            if health_score < 30:  # Lower threshold for healthy -> warning
                status = 'warning'
            else:
                status = 'healthy'
        elif current_status == 'warning':
            # Need more extreme values to change from warning
            if health_score < 15:  # Lower threshold for warning -> critical
                status = 'critical'
            elif health_score > 50:  # Higher threshold for warning -> healthy
                status = 'healthy'
            else:
                status = 'warning'
        else:  # critical
            # Need higher threshold to recover from critical
            if health_score > 40:  # Higher threshold for critical -> warning
                status = 'warning'
            else:
                status = 'critical'
        
        # Only update status - ML predictions are handled separately
        cursor.execute('''
            UPDATE equipment 
            SET status = ?
            WHERE id = ?
        ''', (status, equipment_id))
        
        conn.commit()
        conn.close()
        
        return status
    
    def check_and_create_alerts(self, equipment_id, sensors, health_score, failure_probability, status):
        """Check for alert conditions and create alerts"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Check for various alert conditions
        alert_conditions = []
        
        # Health threshold alerts
        health_status = SensorThresholds.get_health_status(health_score)
        if health_status in ['critical', 'warning']:
            alert_conditions.append({
                'severity': health_status,
                'sensor_trigger': 'health_threshold',
                'description': f'Health score {health_status}: {health_score:.1f}%'
            })
        
        # Temperature alerts using consistent thresholds
        temp_status = SensorThresholds.get_temperature_status(sensors['temperature'])
        if temp_status == 'critical':
            alert_conditions.append({
                'severity': 'critical',
                'sensor_trigger': 'temperature_anomaly',
                'description': f'Temperature critically {("high" if sensors["temperature"] > SensorThresholds.TEMPERATURE["normal_max"] else "low")}: {sensors["temperature"]:.1f}°C'
            })
        elif temp_status == 'warning':
            alert_conditions.append({
                'severity': 'warning',
                'sensor_trigger': 'temperature_anomaly',
                'description': f'Temperature {("elevated" if sensors["temperature"] > SensorThresholds.TEMPERATURE["normal_max"] else "low")}: {sensors["temperature"]:.1f}°C'
            })
        
        # Vibration alerts using consistent thresholds
        vib_status = SensorThresholds.get_vibration_status(sensors['vibration'])
        if vib_status == 'critical':
            alert_conditions.append({
                'severity': 'critical',
                'sensor_trigger': 'vibration_anomaly',
                'description': f'Vibration critically {("high" if sensors["vibration"] > SensorThresholds.VIBRATION["normal_max"] else "low")}: {sensors["vibration"]:.1f} mm/s'
            })
        elif vib_status == 'warning':
            alert_conditions.append({
                'severity': 'warning',
                'sensor_trigger': 'vibration_anomaly',
                'description': f'Vibration {("elevated" if sensors["vibration"] > SensorThresholds.VIBRATION["normal_max"] else "low")}: {sensors["vibration"]:.1f} mm/s'
            })
        
        # Pressure alerts using consistent thresholds
        press_status = SensorThresholds.get_pressure_status(sensors['pressure'])
        if press_status == 'critical':
            alert_conditions.append({
                'severity': 'critical',
                'sensor_trigger': 'pressure_anomaly',
                'description': f'Pressure critically {("high" if sensors["pressure"] > SensorThresholds.PRESSURE["normal_max"] else "low")}: {sensors["pressure"]:.1f} bar'
            })
        elif press_status == 'warning':
            alert_conditions.append({
                'severity': 'warning',
                'sensor_trigger': 'pressure_anomaly',
                'description': f'Pressure {("elevated" if sensors["pressure"] > SensorThresholds.PRESSURE["normal_max"] else "low")}: {sensors["pressure"]:.1f} bar'
            })
        
        # RPM alerts using consistent thresholds
        rpm_status = SensorThresholds.get_rpm_status(sensors['rpm'])
        if rpm_status == 'critical':
            alert_conditions.append({
                'severity': 'critical',
                'sensor_trigger': 'rpm_anomaly',
                'description': f'RPM critically {("high" if sensors["rpm"] > SensorThresholds.RPM["normal_max"] else "low")}: {sensors["rpm"]:.0f} RPM'
            })
        elif rpm_status == 'warning':
            alert_conditions.append({
                'severity': 'warning',
                'sensor_trigger': 'rpm_anomaly',
                'description': f'RPM {("elevated" if sensors["rpm"] > SensorThresholds.RPM["normal_max"] else "low")}: {sensors["rpm"]:.0f} RPM'
            })
        
        # Failure probability alerts using consistent thresholds
        failure_status = SensorThresholds.get_failure_probability_status(failure_probability)
        if failure_status == 'critical':
            alert_conditions.append({
                'severity': 'critical',
                'sensor_trigger': 'failure_probability_high',
                'description': f'High failure probability: {failure_probability:.1f}%'
            })
        elif failure_status == 'warning':
            alert_conditions.append({
                'severity': 'warning',
                'sensor_trigger': 'failure_probability_high',
                'description': f'Elevated failure probability: {failure_probability:.1f}%'
            })
        
        # Check for active anomalies
        anomalies = self.anomaly_injector.get_anomaly_status(equipment_id)
        for anomaly in anomalies:
            alert_conditions.append({
                'severity': 'warning',
                'sensor_trigger': 'anomaly_detected',
                'description': f'Anomaly detected: {anomaly["description"]}'
            })
        
        # Create alerts for new conditions
        for condition in alert_conditions:
            # Check if similar alert already exists (increased throttling to 30 minutes)
            cursor.execute('''
                SELECT id FROM alerts 
                WHERE equipment_id = ? AND sensor_trigger = ? AND status = 'active'
                AND created_at > datetime('now', '-30 minutes')
            ''', (equipment_id, condition['sensor_trigger']))
            
            if not cursor.fetchone():
                # Create new alert
                cursor.execute('''
                    INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                    VALUES (?, ?, ?, 'active', ?, ?)
                ''', (equipment_id, condition['sensor_trigger'], condition['severity'], 
                     failure_probability, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_sensor_thresholds(self, sensor_type):
        """Get consistent thresholds for a sensor type"""
        if sensor_type == 'temperature':
            return {
                'min': SensorThresholds.TEMPERATURE['warning_low'],
                'max': SensorThresholds.TEMPERATURE['warning_high']
            }
        elif sensor_type == 'vibration':
            return {
                'min': SensorThresholds.VIBRATION['warning_low'],
                'max': SensorThresholds.VIBRATION['warning_high']
            }
        elif sensor_type == 'pressure':
            return {
                'min': SensorThresholds.PRESSURE['warning_low'],
                'max': SensorThresholds.PRESSURE['warning_high']
            }
        elif sensor_type == 'rpm':
            return {
                'min': SensorThresholds.RPM['warning_low'],
                'max': SensorThresholds.RPM['warning_high']
            }
        else:
            return {'min': None, 'max': None}
    
    def cleanup_old_alerts(self):
        """Clean up old resolved alerts to prevent database bloat"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Delete resolved alerts older than 7 days
        cursor.execute('''
            DELETE FROM alerts 
            WHERE status = 'resolved' 
            AND created_at < datetime('now', '-7 days')
        ''')
        
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} old resolved alerts")
        
        conn.commit()
        conn.close()
    
    def simulate_data_generation(self):
        """Main simulation loop with anomaly injection"""
        print("🚀 Enhanced IoT Simulator with Anomaly Injection started!")
        
        while self.running:
            self.cycle_count += 1
            
            for equipment_id in self.equipment_configs.keys():
                try:
                    # Generate sensor data with anomalies
                    sensors = self.generate_realistic_sensor_data(equipment_id)
                    
                    # Calculate basic health score for status determination only
                    health_score = self.calculate_health_score(sensors)
                    
                    # Update equipment status (real-time only)
                    status = self.update_equipment_status(equipment_id, health_score, 0)
                    
                    # Check for alerts based on sensor data
                    self.check_and_create_alerts(equipment_id, sensors, health_score, 0, status)
                    
                    # Insert sensor data
                    conn = self.get_db_connection()
                    cursor = conn.cursor()
                    
                    for sensor_type, value in sensors.items():
                        # Get thresholds for this sensor type
                        thresholds = self.get_sensor_thresholds(sensor_type)
                        
                        cursor.execute('''
                            INSERT INTO sensor_data (equipment_id, sensor_type, value, threshold_min, threshold_max, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (equipment_id, sensor_type, value, thresholds['min'], thresholds['max'], datetime.now().isoformat()))
                    
                    conn.commit()
                    conn.close()
                    
                except Exception as e:
                    print(f"Error processing equipment {equipment_id}: {e}")
            
            # Log cycle information
            if self.cycle_count % 10 == 0:
                print(f"🔄 Cycle {self.cycle_count}: Generated data for {len(self.equipment_configs)} equipment")
                
                # Log active anomalies
                total_anomalies = sum(len(anomalies) for anomalies in self.anomaly_injector.active_anomalies.values())
                if total_anomalies > 0:
                    print(f"⚠️  Active anomalies: {total_anomalies}")
            
            # Clean up old alerts every 100 cycles (about every 100 seconds)
            if self.cycle_count % 100 == 0:
                self.cleanup_old_alerts()
            
            # Wait 1 second before next data generation
            time.sleep(1)
    
    def start(self):
        """Start the simulator"""
        if not self.running:
            self.running = True
            self.simulator_thread = threading.Thread(target=self.simulate_data_generation)
            self.simulator_thread.daemon = True
            self.simulator_thread.start()
            print("✅ Enhanced IoT Simulator started!")
    
    def stop(self):
        """Stop the simulator"""
        self.running = False
        print("⏹️  Enhanced IoT Simulator stopped!")

# Global simulator instance
enhanced_simulator = EnhancedIoT_Simulator()
