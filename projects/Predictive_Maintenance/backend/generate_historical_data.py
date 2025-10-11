#!/usr/bin/env python3
"""
Comprehensive Data Generation Script
Creates historical sensor data with various anomaly patterns for ML training
"""

import sqlite3
import random
import numpy as np
from datetime import datetime, timedelta
import json

class HistoricalDataGenerator:
    def __init__(self, db_path='predictive_maintenance.db'):
        self.db_path = db_path
        
        # Equipment configurations
        self.equipment_configs = {
            1: {'name': 'Pump-001', 'type': 'Centrifugal Pump'},
            2: {'name': 'Compressor-002', 'type': 'Air Compressor'},
            3: {'name': 'Motor-003', 'type': 'Electric Motor'}
        }
        
        # Anomaly patterns for historical data
        self.anomaly_patterns = {
            'normal_operation': {
                'probability': 0.70,  # 70% normal operation
                'temperature_range': (60, 80),
                'vibration_range': (1.0, 2.5),
                'pressure_range': (18, 25),
                'rpm_range': (1700, 1900)
            },
            'gradual_degradation': {
                'probability': 0.15,  # 15% gradual degradation
                'temperature_trend': 0.1,  # Gradual increase
                'vibration_trend': 0.05,
                'pressure_trend': -0.02,
                'rpm_trend': 0
            },
            'intermittent_issues': {
                'probability': 0.10,  # 10% intermittent issues
                'temperature_spikes': (10, 30),
                'vibration_spikes': (2, 5),
                'pressure_drops': (3, 8),
                'rpm_fluctuations': (50, 150)
            },
            'severe_anomalies': {
                'probability': 0.05,  # 5% severe anomalies
                'temperature_spikes': (30, 60),
                'vibration_spikes': (5, 10),
                'pressure_drops': (8, 15),
                'rpm_fluctuations': (150, 300)
            }
        }
    
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_historical_sensor_data(self, equipment_id, start_date, end_date, interval_minutes=5):
        """Generate historical sensor data for ML training"""
        print(f"📊 Generating historical data for {self.equipment_configs[equipment_id]['name']}")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing historical data for this equipment
        cursor.execute('DELETE FROM sensor_data WHERE equipment_id = ?', (equipment_id,))
        
        current_time = start_date
        data_points = []
        
        # Base values for equipment
        base_values = {
            1: {'temperature': 70, 'vibration': 1.5, 'pressure': 22, 'rpm': 1800},
            2: {'temperature': 75, 'vibration': 2.0, 'pressure': 25, 'rpm': 2200},
            3: {'temperature': 65, 'vibration': 1.2, 'pressure': 18, 'rpm': 1500}
        }
        
        base = base_values[equipment_id]
        cycle_count = 0
        
        while current_time <= end_date:
            cycle_count += 1
            
            # Determine anomaly pattern for this cycle
            pattern = self._select_anomaly_pattern()
            
            # Generate sensor data based on pattern
            sensors = self._generate_sensor_values(base, pattern, cycle_count)
            
            # Calculate health score and failure probability
            health_score = self._calculate_health_score(sensors)
            failure_probability = self._calculate_failure_probability(sensors, health_score)
            
            # Store data point
            data_point = {
                'equipment_id': equipment_id,
                'timestamp': current_time.isoformat(),
                'sensors': sensors,
                'health_score': health_score,
                'failure_probability': failure_probability,
                'pattern': pattern
            }
            data_points.append(data_point)
            
            # Insert sensor data
            for sensor_type, value in sensors.items():
                cursor.execute('''
                    INSERT INTO sensor_data (equipment_id, sensor_type, value, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (equipment_id, sensor_type, value, current_time.isoformat()))
            
            # Update equipment status periodically
            if cycle_count % 12 == 0:  # Every hour
                status = self._determine_status(health_score, failure_probability)
                cursor.execute('''
                    UPDATE equipment 
                    SET health_score = ?, failure_probability = ?, status = ?
                    WHERE id = ?
                ''', (health_score, failure_probability, status, equipment_id))
                
                # Create alerts if needed
                self._create_historical_alerts(cursor, equipment_id, sensors, health_score, failure_probability, current_time)
            
            current_time += timedelta(minutes=interval_minutes)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Generated {len(data_points)} data points for {self.equipment_configs[equipment_id]['name']}")
        return data_points
    
    def _select_anomaly_pattern(self):
        """Select anomaly pattern based on probabilities"""
        rand = random.random()
        cumulative = 0
        
        for pattern_name, config in self.anomaly_patterns.items():
            cumulative += config['probability']
            if rand <= cumulative:
                return pattern_name
        
        return 'normal_operation'
    
    def _generate_sensor_values(self, base_values, pattern, cycle_count):
        """Generate sensor values based on pattern"""
        sensors = {}
        
        if pattern == 'normal_operation':
            config = self.anomaly_patterns['normal_operation']
            sensors['temperature'] = random.uniform(config['temperature_range'][0], config['temperature_range'][1])
            sensors['vibration'] = random.uniform(config['vibration_range'][0], config['vibration_range'][1])
            sensors['pressure'] = random.uniform(config['pressure_range'][0], config['pressure_range'][1])
            sensors['rpm'] = random.uniform(config['rpm_range'][0], config['rpm_range'][1])
            
        elif pattern == 'gradual_degradation':
            config = self.anomaly_patterns['gradual_degradation']
            sensors['temperature'] = base_values['temperature'] + (config['temperature_trend'] * cycle_count) + random.uniform(-2, 2)
            sensors['vibration'] = base_values['vibration'] + (config['vibration_trend'] * cycle_count) + random.uniform(-0.1, 0.1)
            sensors['pressure'] = base_values['pressure'] + (config['pressure_trend'] * cycle_count) + random.uniform(-0.5, 0.5)
            sensors['rpm'] = base_values['rpm'] + (config['rpm_trend'] * cycle_count) + random.uniform(-25, 25)
            
        elif pattern == 'intermittent_issues':
            config = self.anomaly_patterns['intermittent_issues']
            # Random spikes/drops
            temp_spike = random.uniform(0, config['temperature_spikes'][1]) if random.random() < 0.3 else 0
            vib_spike = random.uniform(0, config['vibration_spikes'][1]) if random.random() < 0.3 else 0
            press_drop = random.uniform(0, config['pressure_drops'][1]) if random.random() < 0.3 else 0
            rpm_fluct = random.uniform(-config['rpm_fluctuations'][1], config['rpm_fluctuations'][1]) if random.random() < 0.3 else 0
            
            sensors['temperature'] = base_values['temperature'] + temp_spike + random.uniform(-2, 2)
            sensors['vibration'] = base_values['vibration'] + vib_spike + random.uniform(-0.1, 0.1)
            sensors['pressure'] = base_values['pressure'] - press_drop + random.uniform(-0.5, 0.5)
            sensors['rpm'] = base_values['rpm'] + rpm_fluct + random.uniform(-25, 25)
            
        elif pattern == 'severe_anomalies':
            config = self.anomaly_patterns['severe_anomalies']
            # Severe spikes/drops
            temp_spike = random.uniform(config['temperature_spikes'][0], config['temperature_spikes'][1])
            vib_spike = random.uniform(config['vibration_spikes'][0], config['vibration_spikes'][1])
            press_drop = random.uniform(config['pressure_drops'][0], config['pressure_drops'][1])
            rpm_fluct = random.uniform(-config['rpm_fluctuations'][1], config['rpm_fluctuations'][1])
            
            sensors['temperature'] = base_values['temperature'] + temp_spike + random.uniform(-3, 3)
            sensors['vibration'] = base_values['vibration'] + vib_spike + random.uniform(-0.2, 0.2)
            sensors['pressure'] = base_values['pressure'] - press_drop + random.uniform(-1, 1)
            sensors['rpm'] = base_values['rpm'] + rpm_fluct + random.uniform(-50, 50)
        
        # Ensure realistic bounds
        sensors['temperature'] = max(20, min(120, sensors['temperature']))
        sensors['vibration'] = max(0.1, min(15, sensors['vibration']))
        sensors['pressure'] = max(5, min(50, sensors['pressure']))
        sensors['rpm'] = max(500, min(3000, sensors['rpm']))
        
        return sensors
    
    def _calculate_health_score(self, sensors):
        """Calculate health score based on sensor data"""
        # Normalize sensor values to 0-100 scale
        temp_score = max(0, 100 - (sensors['temperature'] - 60) * 2)
        vib_score = max(0, 100 - (sensors['vibration'] - 1) * 20)
        press_score = max(0, 100 - abs(sensors['pressure'] - 20) * 3)
        rpm_score = max(0, 100 - abs(sensors['rpm'] - 1800) * 0.05)
        
        # Weighted average
        health_score = (temp_score * 0.3 + vib_score * 0.3 + press_score * 0.2 + rpm_score * 0.2)
        return max(0, min(100, health_score))
    
    def _calculate_failure_probability(self, sensors, health_score):
        """Calculate failure probability based on sensor data and health score"""
        # Base failure probability from health score
        base_prob = (100 - health_score) / 100 * 40  # Max 40% from health
        
        # Additional factors
        temp_factor = max(0, (sensors['temperature'] - 80) * 2)
        vib_factor = max(0, (sensors['vibration'] - 3) * 5)
        press_factor = max(0, abs(sensors['pressure'] - 20) * 1)
        
        failure_prob = base_prob + temp_factor + vib_factor + press_factor
        return max(0, min(100, failure_prob))
    
    def _determine_status(self, health_score, failure_probability):
        """Determine equipment status"""
        if health_score < 30 or failure_probability > 80:
            return 'critical'
        elif health_score < 60 or failure_probability > 50:
            return 'warning'
        else:
            return 'healthy'
    
    def _create_historical_alerts(self, cursor, equipment_id, sensors, health_score, failure_probability, timestamp):
        """Create historical alerts based on sensor data"""
        # Health threshold alerts
        if health_score < 40:
            severity = 'critical' if health_score < 20 else 'warning'
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'health_threshold', ?, 'active', ?, ?)
            ''', (equipment_id, severity, failure_probability, timestamp.isoformat()))
        
        # Temperature alerts
        if sensors['temperature'] > 90:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'temperature_high', 'critical', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
        elif sensors['temperature'] > 80:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'temperature_high', 'warning', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
        
        # Vibration alerts
        if sensors['vibration'] > 5:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'vibration_high', 'critical', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
        elif sensors['vibration'] > 3:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'vibration_high', 'warning', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
        
        # Pressure alerts
        if sensors['pressure'] < 10 or sensors['pressure'] > 40:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'pressure_anomaly', 'critical', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
        elif sensors['pressure'] < 15 or sensors['pressure'] > 35:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'pressure_anomaly', 'warning', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
        
        # Failure probability alerts
        if failure_probability > 70:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'failure_probability_high', 'critical', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
        elif failure_probability > 50:
            cursor.execute('''
                INSERT INTO alerts (equipment_id, sensor_trigger, severity, status, failure_probability, created_at)
                VALUES (?, 'failure_probability_high', 'warning', 'active', ?, ?)
            ''', (equipment_id, failure_probability, timestamp.isoformat()))
    
    def generate_comprehensive_dataset(self, days_back=30):
        """Generate comprehensive dataset for ML training"""
        print(f"🚀 Generating comprehensive dataset for last {days_back} days")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        total_data_points = 0
        total_alerts = 0
        
        for equipment_id in self.equipment_configs.keys():
            # Generate data for each equipment
            data_points = self.generate_historical_sensor_data(equipment_id, start_date, end_date)
            total_data_points += len(data_points)
            
            # Count alerts for this equipment
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE equipment_id = ?', (equipment_id,))
            equipment_alerts = cursor.fetchone()[0]
            total_alerts += equipment_alerts
            conn.close()
        
        print(f"✅ Dataset generation complete!")
        print(f"📊 Total data points: {total_data_points}")
        print(f"🚨 Total alerts: {total_alerts}")
        print(f"📈 Average data points per equipment: {total_data_points // len(self.equipment_configs)}")
        print(f"📈 Average alerts per equipment: {total_alerts // len(self.equipment_configs)}")
        
        return {
            'total_data_points': total_data_points,
            'total_alerts': total_alerts,
            'equipment_count': len(self.equipment_configs),
            'days_covered': days_back
        }
    
    def generate_anomaly_focused_dataset(self, days_back=7):
        """Generate dataset focused on anomalies for better ML training"""
        print(f"⚠️  Generating anomaly-focused dataset for last {days_back} days")
        
        # Increase anomaly probabilities
        original_probabilities = {}
        for pattern_name, config in self.anomaly_patterns.items():
            original_probabilities[pattern_name] = config['probability']
        
        # Adjust probabilities for more anomalies
        self.anomaly_patterns['normal_operation']['probability'] = 0.50  # Reduce normal operation
        self.anomaly_patterns['gradual_degradation']['probability'] = 0.25  # Increase degradation
        self.anomaly_patterns['intermittent_issues']['probability'] = 0.15  # Increase intermittent issues
        self.anomaly_patterns['severe_anomalies']['probability'] = 0.10  # Increase severe anomalies
        
        # Generate dataset
        result = self.generate_comprehensive_dataset(days_back)
        
        # Restore original probabilities
        for pattern_name, config in self.anomaly_patterns.items():
            config['probability'] = original_probabilities[pattern_name]
        
        print(f"✅ Anomaly-focused dataset generation complete!")
        return result

def main():
    """Main function to generate historical data"""
    print("🎯 Historical Data Generation for ML Training")
    print("=" * 60)
    
    generator = HistoricalDataGenerator()
    
    # Generate comprehensive dataset
    print("\n📊 Generating comprehensive dataset...")
    comprehensive_result = generator.generate_comprehensive_dataset(days_back=30)
    
    # Generate anomaly-focused dataset
    print("\n⚠️  Generating anomaly-focused dataset...")
    anomaly_result = generator.generate_anomaly_focused_dataset(days_back=7)
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 DATA GENERATION SUMMARY")
    print("=" * 60)
    print(f"Comprehensive Dataset: {comprehensive_result['total_data_points']} points, {comprehensive_result['total_alerts']} alerts")
    print(f"Anomaly Dataset: {anomaly_result['total_data_points']} points, {anomaly_result['total_alerts']} alerts")
    print(f"Total Equipment: {comprehensive_result['equipment_count']}")
    print(f"Days Covered: {comprehensive_result['days_covered']} + {anomaly_result['days_covered']}")
    
    print("\n🎉 Historical data generation complete!")
    print("🚀 Ready for ML model training with comprehensive dataset!")

if __name__ == "__main__":
    main()
