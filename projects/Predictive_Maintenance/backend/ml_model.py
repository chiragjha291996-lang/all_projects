"""
Machine Learning Model for Predictive Maintenance
Handles model training, retraining, and prediction
"""

import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta
import json

class PredictiveMaintenanceModel:
    def __init__(self, db_path='predictive_maintenance.db'):
        self.db_path = db_path
        self.model_path = 'models/'
        self.scaler_path = 'models/scaler.pkl'
        
        # Create models directory
        os.makedirs(self.model_path, exist_ok=True)
        
        # Model components
        self.health_model = None  # RandomForest for health score prediction
        self.failure_model = None  # RandomForest for failure probability
        self.scaler = StandardScaler()
        
        # Model performance tracking
        self.model_performance = {
            'health_model': {'mse': None, 'r2': None, 'last_trained': None},
            'failure_model': {'accuracy': None, 'precision': None, 'recall': None, 'last_trained': None}
        }
    
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def prepare_training_data(self, days_back=30):
        """Prepare training data from historical sensor data"""
        conn = self.get_db_connection()
        
        # Get sensor data from last N days
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        query = """
        SELECT 
            sd.equipment_id,
            sd.sensor_type,
            sd.value,
            sd.timestamp,
            e.health_score,
            e.failure_probability,
            e.status
        FROM sensor_data sd
        JOIN equipment e ON sd.equipment_id = e.id
        WHERE sd.timestamp >= ?
        ORDER BY sd.timestamp
        """
        
        df = pd.read_sql_query(query, conn, params=[cutoff_date])
        conn.close()
        
        if df.empty:
            return None, None
        
        # Pivot sensor data to get features
        sensor_pivot = df.pivot_table(
            index=['equipment_id', 'timestamp'], 
            columns='sensor_type', 
            values='value', 
            fill_value=0
        ).reset_index()
        
        # Add equipment metadata
        equipment_data = df[['equipment_id', 'timestamp', 'health_score', 'failure_probability', 'status']].drop_duplicates()
        
        # Merge sensor and equipment data
        training_data = sensor_pivot.merge(equipment_data, on=['equipment_id', 'timestamp'])
        
        # Create features
        features = ['temperature', 'vibration', 'pressure', 'rpm']
        feature_cols = [col for col in features if col in training_data.columns]
        
        # Fill missing sensor values with median
        for col in feature_cols:
            training_data[col] = training_data[col].fillna(training_data[col].median())
        
        # Add derived features
        training_data['temp_pressure_ratio'] = training_data['temperature'] / (training_data['pressure'] + 1)
        training_data['vibration_rpm_ratio'] = training_data['vibration'] / (training_data['rpm'] + 1)
        
        # Fix timestamp parsing
        try:
            training_data['equipment_age'] = (datetime.now() - pd.to_datetime(training_data['timestamp'], format='mixed')).dt.days
        except:
            training_data['equipment_age'] = 30  # Default age if parsing fails
        
        # Prepare feature matrix
        feature_cols.extend(['temp_pressure_ratio', 'vibration_rpm_ratio', 'equipment_age'])
        X = training_data[feature_cols].fillna(0)
        
        # Prepare targets
        y_health = training_data['health_score']
        y_failure = (training_data['failure_probability'] > 0.7).astype(int)  # Binary classification
        
        return X, y_health, y_failure, feature_cols
    
    def train_health_model(self, X, y_health):
        """Train Random Forest model for health score prediction"""
        print("Training health score prediction model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_health, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.health_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.health_model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.health_model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = self.health_model.score(X_test_scaled, y_test)
        
        # Update performance tracking
        self.model_performance['health_model'] = {
            'mse': mse,
            'r2': r2,
            'last_trained': datetime.now().isoformat()
        }
        
        print(f"Health Model - MSE: {mse:.4f}, R²: {r2:.4f}")
        return mse, r2
    
    def train_failure_model(self, X, y_failure):
        """Train Random Forest model for failure probability prediction"""
        print("Training failure probability prediction model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_failure, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.failure_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.failure_model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.failure_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get detailed metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Update performance tracking
        self.model_performance['failure_model'] = {
            'accuracy': accuracy,
            'precision': report['weighted avg']['precision'],
            'recall': report['weighted avg']['recall'],
            'last_trained': datetime.now().isoformat()
        }
        
        print(f"Failure Model - Accuracy: {accuracy:.4f}")
        return accuracy, report
    
    def train_models(self, days_back=30):
        """Train both health and failure prediction models"""
        print("Starting model training...")
        
        # Prepare training data
        data = self.prepare_training_data(days_back)
        if data[0] is None:
            print("No training data available")
            return False
        
        X, y_health, y_failure, feature_cols = data
        
        if len(X) < 100:  # Need minimum data points
            print(f"Insufficient training data: {len(X)} samples (minimum 100 required)")
            return False
        
        print(f"Training with {len(X)} samples and {len(feature_cols)} features")
        
        # Train models
        health_mse, health_r2 = self.train_health_model(X, y_health)
        failure_acc, failure_report = self.train_failure_model(X, y_failure)
        
        # Save models
        self.save_models()
        
        # Save feature columns for prediction
        with open(f"{self.model_path}/feature_columns.json", 'w') as f:
            json.dump(feature_cols, f)
        
        print("Model training completed successfully!")
        return True
    
    def save_models(self):
        """Save trained models to disk"""
        if self.health_model:
            joblib.dump(self.health_model, f"{self.model_path}/health_model.pkl")
        
        if self.failure_model:
            joblib.dump(self.failure_model, f"{self.model_path}/failure_model.pkl")
        
        joblib.dump(self.scaler, self.scaler_path)
        
        # Save performance metrics
        with open(f"{self.model_path}/performance.json", 'w') as f:
            json.dump(self.model_performance, f, indent=2)
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            if os.path.exists(f"{self.model_path}/health_model.pkl"):
                self.health_model = joblib.load(f"{self.model_path}/health_model.pkl")
            
            if os.path.exists(f"{self.model_path}/failure_model.pkl"):
                self.failure_model = joblib.load(f"{self.model_path}/failure_model.pkl")
            
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
            
            # Load performance metrics
            if os.path.exists(f"{self.model_path}/performance.json"):
                with open(f"{self.model_path}/performance.json", 'r') as f:
                    self.model_performance = json.load(f)
            
            print("Models loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    
    def predict_health_score(self, sensor_data):
        """Predict health score for given sensor data"""
        if not self.health_model:
            return None
        
        # Load feature columns
        try:
            with open(f"{self.model_path}/feature_columns.json", 'r') as f:
                feature_cols = json.load(f)
        except:
            feature_cols = ['temperature', 'vibration', 'pressure', 'rpm']
        
        # Prepare features in the exact order as training
        features = []
        
        # Core sensor features first
        core_features = ['temperature', 'vibration', 'pressure', 'rpm']
        for col in core_features:
            if col in sensor_data:
                features.append(sensor_data[col])
            else:
                features.append(0)  # Default value
        
        # Add derived features in the same order as training
        features.append(features[0] / (features[2] + 1))  # temp_pressure_ratio
        features.append(features[1] / (features[3] + 1))  # vibration_rpm_ratio
        features.append(30)  # equipment_age (default)
        
        # Scale features and predict
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        prediction = self.health_model.predict(X_scaled)[0]
        if prediction is None:
            return 50.0  # Default health score
        return max(0, min(100, float(prediction)))  # Clamp between 0-100
    
    def predict_failure_probability(self, sensor_data):
        """Predict failure probability for given sensor data"""
        if not self.failure_model:
            return None
        
        # Load feature columns
        try:
            with open(f"{self.model_path}/feature_columns.json", 'r') as f:
                feature_cols = json.load(f)
        except:
            feature_cols = ['temperature', 'vibration', 'pressure', 'rpm']
        
        # Prepare features in the exact order as training
        features = []
        
        # Core sensor features first
        core_features = ['temperature', 'vibration', 'pressure', 'rpm']
        for col in core_features:
            if col in sensor_data:
                features.append(sensor_data[col])
            else:
                features.append(0)  # Default value
        
        # Add derived features in the same order as training
        features.append(features[0] / (features[2] + 1))  # temp_pressure_ratio
        features.append(features[1] / (features[3] + 1))  # vibration_rpm_ratio
        features.append(30)  # equipment_age (default)
        
        # Scale features and predict
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Get probability of failure (class 1)
        probabilities = self.failure_model.predict_proba(X_scaled)[0]
        if len(probabilities) > 1:
            probability = probabilities[1]  # Class 1 (failure)
        else:
            probability = probabilities[0]  # Single class case
        
        if probability is None:
            return 25.0  # Default failure probability
        return float(probability) * 100  # Convert to percentage
    
    def get_model_performance(self):
        """Get current model performance metrics"""
        return self.model_performance
    
    def should_retrain(self, days_threshold=7):
        """Check if models should be retrained based on age"""
        if not self.model_performance['health_model']['last_trained']:
            return True
        
        last_trained = datetime.fromisoformat(self.model_performance['health_model']['last_trained'])
        days_since_training = (datetime.now() - last_trained).days
        
        return days_since_training >= days_threshold
    
    def retrain_if_needed(self):
        """Automatically retrain models if needed"""
        if self.should_retrain():
            print("Models are outdated, retraining...")
            return self.train_models()
        return False

# Global model instance
ml_model = PredictiveMaintenanceModel()
