from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import threading
import time
import random
import numpy as np
from datetime import datetime, timedelta
import os
from enhanced_simulator import enhanced_simulator
from realistic_ml_model import realistic_ml_model
from sensor_thresholds import SensorThresholds

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'predictive_maintenance.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Equipment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'healthy',
            health_score REAL DEFAULT 100.0,
            failure_probability REAL DEFAULT 0.0,
            failure_prediction TEXT DEFAULT 'No failure predicted',
            prediction_confidence TEXT DEFAULT 'Low',
            prediction_urgency TEXT DEFAULT 'SAFE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sensor data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER,
            sensor_type TEXT NOT NULL,
            value REAL NOT NULL,
            threshold_min REAL,
            threshold_max REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (equipment_id) REFERENCES equipment (id)
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER,
            severity TEXT NOT NULL,
            failure_probability REAL,
            sensor_trigger TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged_at TIMESTAMP,
            FOREIGN KEY (equipment_id) REFERENCES equipment (id)
        )
    ''')
    
    # System metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_alerts INTEGER DEFAULT 0,
            active_alerts INTEGER DEFAULT 0,
            resolved_alerts INTEGER DEFAULT 0,
            uptime_percentage REAL DEFAULT 100.0,
            predictions_today INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_initial_data():
    """Seed the database with initial equipment data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if equipment already exists
    cursor.execute('SELECT COUNT(*) FROM equipment')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Insert initial equipment
    equipment_data = [
        ('Pump-001', 'Pump', 'healthy', 95.0, 5.0),
        ('Compressor-002', 'Compressor', 'healthy', 88.0, 12.0),
        ('Conveyor-003', 'Conveyor Belt', 'healthy', 92.0, 8.0)
    ]
    
    cursor.executemany('''
        INSERT INTO equipment (name, type, status, health_score, failure_probability)
        VALUES (?, ?, ?, ?, ?)
    ''', equipment_data)
    
    # Insert initial system metrics
    cursor.execute('''
        INSERT INTO system_metrics (total_alerts, active_alerts, resolved_alerts, uptime_percentage, predictions_today)
        VALUES (0, 0, 0, 100.0, 0)
    ''')
    
    conn.commit()
    conn.close()

# API Routes

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data including equipment status and system metrics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get equipment data
    cursor.execute('''
        SELECT id, name, type, status, health_score, failure_probability,
               failure_prediction, prediction_confidence, prediction_urgency
        FROM equipment
        ORDER BY id
    ''')
    
    equipment_data = []
    for row in cursor.fetchall():
        equipment_id, name, type_name, status, health_score, failure_probability, failure_prediction, prediction_confidence, prediction_urgency = row
        
        # Determine status color based on urgency
        if prediction_urgency in ['IMMEDIATE', 'URGENT']:
            status_color = 'red'
        elif prediction_urgency in ['SCHEDULE', 'MONITOR']:
            status_color = 'yellow'
        else:
            status_color = 'green'
        
        equipment_data.append({
            'id': equipment_id,
            'name': name,
            'type': type_name,
            'status': status,
            'statusColor': status_color,
            'healthScore': health_score,
            'failureProbability': failure_probability,
            'failurePrediction': failure_prediction,
            'predictionConfidence': prediction_confidence,
            'predictionUrgency': prediction_urgency
        })
    
    # Get system metrics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_alerts,
            SUM(CASE WHEN alerts.status = 'active' THEN 1 ELSE 0 END) as active_alerts,
            SUM(CASE WHEN alerts.status = 'resolved' THEN 1 ELSE 0 END) as resolved_alerts,
            AVG(equipment.health_score) as avg_uptime,
            COUNT(DISTINCT DATE(alerts.created_at)) as predictions_today
        FROM alerts
        LEFT JOIN equipment ON alerts.equipment_id = equipment.id
    ''')
    
    metrics_row = cursor.fetchone()
    if metrics_row:
        total_alerts, active_alerts, resolved_alerts, avg_uptime, predictions_today = metrics_row
    else:
        total_alerts = active_alerts = resolved_alerts = predictions_today = 0
        avg_uptime = 100.0
    
    conn.close()
    
    return jsonify({
        'equipment': equipment_data,
        'metrics': {
            'totalAlerts': total_alerts,
            'activeAlerts': active_alerts,
            'resolvedAlerts': resolved_alerts,
            'uptimePercentage': round(avg_uptime, 1) if avg_uptime else 100.0,
            'predictionsToday': predictions_today
        }
    })

@app.route('/api/equipment/<int:equipment_id>', methods=['GET'])
def get_equipment_detail(equipment_id):
    """Get detailed equipment information"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get equipment basic info
    cursor.execute('''
        SELECT id, name, type, status, health_score, failure_probability
        FROM equipment
        WHERE id = ?
    ''', (equipment_id,))
    
    equipment_row = cursor.fetchone()
    if not equipment_row:
        conn.close()
        return jsonify({'error': 'Equipment not found'}), 404
    
    equipment_id, name, type_name, status, health_score, failure_probability = equipment_row
    
    # Get recent sensor data (last hour)
    cursor.execute('''
        SELECT sensor_type, value, threshold_min, threshold_max, timestamp
        FROM sensor_data
        WHERE equipment_id = ? AND timestamp > datetime('now', '-1 hour')
        ORDER BY timestamp DESC
        LIMIT 100
    ''', (equipment_id,))
    
    sensor_data = {}
    for sensor_type, value, threshold_min, threshold_max, timestamp in cursor.fetchall():
        if sensor_type not in sensor_data:
            sensor_data[sensor_type] = []
        sensor_data[sensor_type].append({
            'value': value,
            'threshold_min': threshold_min,
            'threshold_max': threshold_max,
            'timestamp': timestamp
        })
    
    # Get recent alerts
    cursor.execute('''
        SELECT id, severity, failure_probability, sensor_trigger, status, created_at
        FROM alerts
        WHERE equipment_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (equipment_id,))
    
    alerts = []
    for alert_id, severity, prob, trigger, alert_status, created_at in cursor.fetchall():
        alerts.append({
            'id': alert_id,
            'severity': severity,
            'failureProbability': prob,
            'sensorTrigger': trigger,
            'status': alert_status,
            'createdAt': created_at
        })
    
    conn.close()
    
    return jsonify({
        'equipment': {
            'id': equipment_id,
            'name': name,
            'type': type_name,
            'status': status,
            'healthScore': health_score,
            'failureProbability': failure_probability
        },
        'sensorData': sensor_data,
        'alerts': alerts
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts with optional filtering"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get query parameters
    equipment_id = request.args.get('equipment_id')
    severity = request.args.get('severity')
    status = request.args.get('status')
    
    # Build query
    query = '''
        SELECT a.id, a.equipment_id, e.name as equipment_name, a.severity, 
               a.failure_probability, a.sensor_trigger, a.status, a.created_at, a.acknowledged_at
        FROM alerts a
        JOIN equipment e ON a.equipment_id = e.id
        WHERE 1=1
    '''
    params = []
    
    if equipment_id:
        query += ' AND a.equipment_id = ?'
        params.append(equipment_id)
    
    if severity:
        query += ' AND a.severity = ?'
        params.append(severity)
    
    if status:
        query += ' AND a.status = ?'
        params.append(status)
    
    query += ' ORDER BY a.created_at DESC'
    
    cursor.execute(query, params)
    
    alerts = []
    for row in cursor.fetchall():
        alert_id, eq_id, eq_name, sev, prob, trigger, alert_status, created_at, ack_at = row
        alerts.append({
            'id': alert_id,
            'equipmentId': eq_id,
            'equipmentName': eq_name,
            'severity': sev,
            'failureProbability': prob,
            'sensorTrigger': trigger,
            'status': alert_status,
            'createdAt': created_at,
            'acknowledgedAt': ack_at
        })
    
    conn.close()
    
    return jsonify({'alerts': alerts})

@app.route('/api/simulator/start', methods=['POST'])
def start_simulator():
    """Start the enhanced IoT simulator with anomaly injection"""
    try:
        enhanced_simulator.start()
        return jsonify({'success': True, 'message': 'Enhanced IoT Simulator with anomaly injection started!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting simulator: {str(e)}'}), 500

@app.route('/api/simulator/stop', methods=['POST'])
def stop_simulator():
    """Stop the enhanced IoT simulator"""
    try:
        enhanced_simulator.stop()
        return jsonify({'success': True, 'message': 'Enhanced IoT Simulator stopped!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping simulator: {str(e)}'}), 500

@app.route('/api/simulator/status', methods=['GET'])
def get_simulator_status():
    """Get enhanced simulator status"""
    return jsonify({
        'running': enhanced_simulator.running,
        'cycle_count': enhanced_simulator.cycle_count,
        'anomaly_injection': True,
        'active_anomalies': sum(len(anomalies) for anomalies in enhanced_simulator.anomaly_injector.active_anomalies.values())
    })

# ML Model Training Endpoints
@app.route('/api/ml/train', methods=['POST'])
def train_models():
    """Train ML models with incremental learning on new data"""
    try:
        data = request.get_json() or {}
        days_back = data.get('days_back', 7)  # Default to 7 days for incremental learning
        
        # Load existing models first
        realistic_ml_model.load_models()
        
        # Train models with incremental approach
        success = realistic_ml_model.train_models_incremental(days_back)
        
        if success:
            performance = realistic_ml_model.get_model_performance()
            warnings = realistic_ml_model.validate_model_performance()
            
            return jsonify({
                'success': True,
                'message': 'Models trained successfully with incremental learning',
                'performance': performance,
                'training_data_days': days_back,
                'warnings': warnings,
                'validation_info': {
                    'cross_validation_used': True,
                    'realistic_accuracy': True,
                    'incremental_learning': True
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Training failed - insufficient data or other error'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Training error: {str(e)}'
        }), 500

@app.route('/api/ml/performance', methods=['GET'])
def get_model_performance():
    """Get current model performance metrics with validation"""
    try:
        realistic_ml_model.load_models()
        performance = realistic_ml_model.get_model_performance()
        warnings = realistic_ml_model.validate_model_performance()
        
        return jsonify({
            'success': True,
            'performance': performance,
            'warnings': warnings,
            'validation_info': {
                'cross_validation_used': True,
                'realistic_accuracy': True,
                'incremental_learning': True
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting performance: {str(e)}'
        }), 500

@app.route('/api/ml/retrain', methods=['POST'])
def retrain_models():
    """Retrain models with new sensor data"""
    try:
        data = request.get_json() or {}
        days_back = data.get('days_back', 7)  # Use recent data for retraining
        
        realistic_ml_model.load_models()
        
        # Always retrain with new data (incremental learning)
        success = realistic_ml_model.train_models_incremental(days_back)
        
        if success:
            performance = realistic_ml_model.get_model_performance()
            warnings = realistic_ml_model.validate_model_performance()
            
            return jsonify({
                'success': True,
                'message': f'Models retrained successfully with last {days_back} days of data',
                'performance': performance,
                'warnings': warnings,
                'retrained': True,
                'validation_info': {
                    'cross_validation_used': True,
                    'realistic_accuracy': True,
                    'incremental_learning': True
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Retraining failed - insufficient new data'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Retraining error: {str(e)}'
        }), 500

@app.route('/api/thresholds', methods=['GET'])
def get_sensor_thresholds():
    """Get consistent sensor thresholds for all equipment"""
    try:
        thresholds = SensorThresholds.get_all_thresholds()
        return jsonify({
            'success': True,
            'thresholds': thresholds,
            'description': 'Consistent sensor thresholds applied across all equipment types'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving thresholds: {str(e)}'
        }), 500

@app.route('/api/ml/predict-all', methods=['POST'])
def predict_all_equipment():
    """Generate ML predictions for all equipment and store in database"""
    try:
        realistic_ml_model.load_models()
        
        if realistic_ml_model.health_model is None or realistic_ml_model.failure_model is None:
            return jsonify({
                'success': False,
                'message': 'Models not trained yet. Please train models first.'
            }), 400
        
        success = realistic_ml_model.predict_and_store_for_all_equipment()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'ML predictions generated and stored for all equipment'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate ML predictions'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating ML predictions: {str(e)}'
        }), 500

@app.route('/api/ml/predict', methods=['POST'])
def predict_with_ml():
    """Make predictions using trained ML models"""
    try:
        data = request.get_json()
        if not data or 'sensor_data' not in data:
            return jsonify({
                'success': False,
                'message': 'Sensor data required'
            }), 400
        
        realistic_ml_model.load_models()
        
        sensor_data = data['sensor_data']
        
        # Make predictions
        health_score = realistic_ml_model.predict_health_score(sensor_data)
        failure_probability = realistic_ml_model.predict_failure_probability(sensor_data)
        
        return jsonify({
            'success': True,
            'predictions': {
                'health_score': health_score,
                'failure_probability': failure_probability
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Prediction error: {str(e)}'
        }), 500

@app.route('/api/ml/status', methods=['GET'])
def get_ml_status():
    """Get ML model status and info"""
    try:
        realistic_ml_model.load_models()
        
        # Check if models exist
        models_exist = realistic_ml_model.health_model is not None and realistic_ml_model.failure_model is not None
        
        # Get performance if available
        performance = realistic_ml_model.get_model_performance()
        warnings = realistic_ml_model.validate_model_performance()
        
        # Check if retraining is needed
        needs_retraining = realistic_ml_model.should_retrain()
        
        return jsonify({
            'success': True,
            'models_trained': models_exist,
            'needs_retraining': needs_retraining,
            'performance': performance,
            'warnings': warnings,
            'validation_info': {
                'cross_validation_used': True,
                'realistic_accuracy': True,
                'incremental_learning': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting ML status: {str(e)}'
        }), 500

@app.route('/api/data/generate-historical', methods=['POST'])
def generate_historical_data():
    """Generate historical data for ML training"""
    try:
        from generate_historical_data import HistoricalDataGenerator
        
        data = request.get_json() or {}
        days_back = data.get('days_back', 30)
        
        generator = HistoricalDataGenerator()
        result = generator.generate_comprehensive_dataset(days_back)
        
        return jsonify({
            'success': True,
            'message': f'Historical data generated successfully',
            'data_points': result['total_data_points'],
            'alerts': result['total_alerts'],
            'equipment_count': result['equipment_count'],
            'days_covered': result['days_covered']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating historical data: {str(e)}'
        }), 500

@app.route('/api/data/generate-anomalies', methods=['POST'])
def generate_anomaly_data():
    """Generate anomaly-focused data for ML training"""
    try:
        from generate_historical_data import HistoricalDataGenerator
        
        data = request.get_json() or {}
        days_back = data.get('days_back', 7)
        
        generator = HistoricalDataGenerator()
        result = generator.generate_anomaly_focused_dataset(days_back)
        
        return jsonify({
            'success': True,
            'message': f'Anomaly-focused data generated successfully',
            'data_points': result['total_data_points'],
            'alerts': result['total_alerts'],
            'equipment_count': result['equipment_count'],
            'days_covered': result['days_covered']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating anomaly data: {str(e)}'
        }), 500

if __name__ == '__main__':
    init_db()
    seed_initial_data()
    enhanced_simulator.start()  # Start enhanced simulator with anomaly injection automatically
    print("Database initialized successfully!")
    print("IoT Simulator started!")
    app.run(debug=True, port=5001)
