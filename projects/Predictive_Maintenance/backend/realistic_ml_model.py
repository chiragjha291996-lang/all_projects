"""
Realistic Machine Learning Model for Predictive Maintenance
Implements incremental learning, proper validation, and realistic accuracy reporting
"""

import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class RealisticPredictiveMaintenanceModel:
    def __init__(self, db_path='predictive_maintenance.db'):
        self.db_path = db_path
        self.model_path = 'models/'
        self.scaler_path = 'models/scaler.pkl'
        
        # Create models directory
        os.makedirs(self.model_path, exist_ok=True)
        
        # Model components
        self.health_model = None
        self.failure_model = None
        self.scaler = StandardScaler()
        
        # Incremental learning parameters
        self.min_samples_for_training = 100
        self.validation_split = 0.2
        self.cv_folds = 5
        
        # Model performance tracking with realistic expectations
        self.model_performance = {
            'health_model': {
                'mse': None, 
                'r2': None, 
                'cv_score_mean': None,
                'cv_score_std': None,
                'last_trained': None,
                'training_samples': 0,
                'validation_samples': 0
            },
            'failure_model': {
                'accuracy': None, 
                'precision': None, 
                'recall': None, 
                'f1_score': None,
                'cv_score_mean': None,
                'cv_score_std': None,
                'last_trained': None,
                'training_samples': 0,
                'validation_samples': 0,
                'confusion_matrix': None
            }
        }
    
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def prepare_training_data(self, days_back=7, include_new_data=True):
        """Prepare training data with focus on recent data"""
        conn = self.get_db_connection()
        
        # Get sensor data from last N days (shorter window for incremental learning)
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
        ORDER BY sd.timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[cutoff_date])
        conn.close()
        
        if df.empty:
            return None, None, None, None
        
        print(f"📊 Retrieved {len(df)} sensor records from last {days_back} days")
        
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
        
        # Add time-based features
        try:
            training_data['timestamp'] = pd.to_datetime(training_data['timestamp'], format='mixed')
            training_data['hour_of_day'] = training_data['timestamp'].dt.hour
            training_data['day_of_week'] = training_data['timestamp'].dt.dayofweek
        except:
            training_data['hour_of_day'] = 12  # Default noon
            training_data['day_of_week'] = 1   # Default Monday
        
        # Prepare feature matrix
        feature_cols.extend(['temp_pressure_ratio', 'vibration_rpm_ratio', 'hour_of_day', 'day_of_week'])
        X = training_data[feature_cols].fillna(0)
        
        # Prepare targets with more realistic thresholds
        y_health = training_data['health_score']
        
        # More realistic failure classification (not 100% accuracy)
        failure_threshold = 0.6  # 60% failure probability threshold
        y_failure = (training_data['failure_probability'] > failure_threshold).astype(int)
        
        print(f"📈 Features: {len(feature_cols)}, Samples: {len(X)}")
        print(f"🎯 Health scores range: {y_health.min():.1f} - {y_health.max():.1f}")
        print(f"⚠️  Failure cases: {y_failure.sum()}/{len(y_failure)} ({y_failure.mean()*100:.1f}%)")
        
        return X, y_health, y_failure, feature_cols
    
    def train_health_model(self, X, y_health):
        """Train health model with proper validation"""
        print("🏥 Training health score prediction model...")
        
        # Split data with time series consideration
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_health, test_size=self.validation_split, random_state=42, stratify=None
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model with more conservative parameters
        self.health_model = RandomForestRegressor(
            n_estimators=50,  # Reduced for faster training
            max_depth=8,      # Reduced to prevent overfitting
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.health_model.fit(X_train_scaled, y_train)
        
        # Cross-validation for more realistic performance estimate
        cv_scores = cross_val_score(
            self.health_model, X_train_scaled, y_train, 
            cv=self.cv_folds, scoring='neg_mean_squared_error'
        )
        
        # Evaluate on test set
        y_pred = self.health_model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = self.health_model.score(X_test_scaled, y_test)
        
        # Update performance tracking
        self.model_performance['health_model'] = {
            'mse': mse,
            'r2': r2,
            'cv_score_mean': -cv_scores.mean(),
            'cv_score_std': cv_scores.std(),
            'last_trained': datetime.now().isoformat(),
            'training_samples': len(X_train),
            'validation_samples': len(X_test)
        }
        
        print(f"✅ Health Model - MSE: {mse:.4f}, R²: {r2:.4f}")
        print(f"📊 CV MSE: {-cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        return mse, r2
    
    def train_failure_model(self, X, y_failure):
        """Train failure model with proper validation"""
        print("⚠️  Training failure probability prediction model...")
        
        # Check if we have enough failure cases
        failure_ratio = y_failure.mean()
        if failure_ratio < 0.05:  # Less than 5% failure cases
            print(f"⚠️  Warning: Only {failure_ratio*100:.1f}% failure cases - model may not be reliable")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_failure, test_size=self.validation_split, random_state=42, stratify=y_failure
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model with class balancing
        self.failure_model = RandomForestClassifier(
            n_estimators=50,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced',  # Handle class imbalance
            random_state=42,
            n_jobs=-1
        )
        
        self.failure_model.fit(X_train_scaled, y_train)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.failure_model, X_train_scaled, y_train, 
            cv=self.cv_folds, scoring='accuracy'
        )
        
        # Evaluate on test set
        y_pred = self.failure_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get detailed metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)
        
        # Update performance tracking
        self.model_performance['failure_model'] = {
            'accuracy': accuracy,
            'precision': report['weighted avg']['precision'],
            'recall': report['weighted avg']['recall'],
            'f1_score': report['weighted avg']['f1-score'],
            'cv_score_mean': cv_scores.mean(),
            'cv_score_std': cv_scores.std(),
            'last_trained': datetime.now().isoformat(),
            'training_samples': len(X_train),
            'validation_samples': len(X_test),
            'confusion_matrix': cm.tolist()
        }
        
        print(f"✅ Failure Model - Accuracy: {accuracy:.4f}")
        print(f"📊 CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        print(f"📈 Precision: {report['weighted avg']['precision']:.4f}")
        print(f"📈 Recall: {report['weighted avg']['recall']:.4f}")
        
        return accuracy, report
    
    def train_models_incremental(self, days_back=7):
        """Train models with incremental learning approach"""
        print("🔄 Starting incremental model training...")
        
        # Prepare training data
        data = self.prepare_training_data(days_back)
        if data[0] is None:
            print("❌ No training data available")
            return False
        
        X, y_health, y_failure, feature_cols = data
        
        if len(X) < self.min_samples_for_training:
            print(f"❌ Insufficient training data: {len(X)} samples (minimum {self.min_samples_for_training} required)")
            return False
        
        print(f"🚀 Training with {len(X)} samples and {len(feature_cols)} features")
        
        # Train models
        health_mse, health_r2 = self.train_health_model(X, y_health)
        failure_acc, failure_report = self.train_failure_model(X, y_failure)
        
        # Save models
        self.save_models()
        
        # Save feature columns for prediction
        with open(f"{self.model_path}/feature_columns.json", 'w') as f:
            json.dump(feature_cols, f)
        
        print("✅ Incremental model training completed!")
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
            
            print("📂 Models loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Error loading models: {e}")
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
        
        # Add derived features
        features.append(features[0] / (features[2] + 1))  # temp_pressure_ratio
        features.append(features[1] / (features[3] + 1))  # vibration_rpm_ratio
        
        # Add time features
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        features.append(current_hour)
        features.append(current_day)
        
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
        
        # Add derived features
        features.append(features[0] / (features[2] + 1))  # temp_pressure_ratio
        features.append(features[1] / (features[3] + 1))  # vibration_rpm_ratio
        
        # Add time features
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        features.append(current_hour)
        features.append(current_day)
        
        # Scale features and predict
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Get probability of failure
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
    
    def validate_model_performance(self):
        """Validate that model performance is realistic"""
        health_perf = self.model_performance['health_model']
        failure_perf = self.model_performance['failure_model']
        
        warnings = []
        
        # Check health model performance
        if health_perf['r2'] and health_perf['r2'] > 0.95:
            warnings.append("Health model R² > 95% - may be overfitting")
        
        # Check failure model performance
        if failure_perf['accuracy'] and failure_perf['accuracy'] > 0.95:
            warnings.append("Failure model accuracy > 95% - may be overfitting")
        
        if failure_perf['cv_score_std'] and failure_perf['cv_score_std'] > 0.1:
            warnings.append("High cross-validation variance - model may be unstable")
        
        return warnings
    
    def should_retrain(self, days_threshold=3):
        """Check if models should be retrained based on age and data freshness"""
        if not self.model_performance['health_model']['last_trained']:
            return True
        
        last_trained = datetime.fromisoformat(self.model_performance['health_model']['last_trained'])
        days_since_training = (datetime.now() - last_trained).days
        
        return days_since_training >= days_threshold
    
    def predict_and_store_for_all_equipment(self):
        """Predict health scores and failure probabilities for all equipment and store in database"""
        import sqlite3
        
        if not self.health_model or not self.failure_model:
            print("⚠️ Models not trained yet. Cannot make predictions.")
            return False
        
        try:
            conn = sqlite3.connect('predictive_maintenance.db')
            cursor = conn.cursor()
            
            # Get all equipment
            cursor.execute('SELECT id FROM equipment')
            equipment_ids = [row[0] for row in cursor.fetchall()]
            
            for equipment_id in equipment_ids:
                # Get latest sensor data for each sensor type
                sensor_data = {}
                latest_timestamp = None
                
                for sensor_type in ['temperature', 'vibration', 'pressure', 'rpm']:
                    cursor.execute('''
                        SELECT value, timestamp
                        FROM sensor_data 
                        WHERE equipment_id = ? AND sensor_type = ?
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    ''', (equipment_id, sensor_type))
                    
                    sensor_row = cursor.fetchone()
                    if not sensor_row:
                        break
                    
                    value, timestamp = sensor_row
                    sensor_data[sensor_type] = value
                    
                    if latest_timestamp is None:
                        latest_timestamp = timestamp
                
                # Ensure we have all required sensors
                if len(sensor_data) < 4:
                    continue
                
                sensor_data['timestamp'] = latest_timestamp
                
                # Predict health score and failure probability
                health_score = self.predict_health_score(sensor_data)
                failure_probability = self.predict_failure_probability(sensor_data)
                
                # Convert to time-based prediction
                prediction_info = self._convert_to_time_prediction(failure_probability, health_score)
                
                # Update equipment table with ML predictions
                cursor.execute('''
                    UPDATE equipment 
                    SET health_score = ?, failure_probability = ?, 
                        failure_prediction = ?, prediction_confidence = ?, prediction_urgency = ?
                    WHERE id = ?
                ''', (
                    round(health_score, 1),  # Trim to 1 decimal
                    prediction_info['probability'],
                    prediction_info['message'],
                    prediction_info['confidence'],
                    prediction_info['urgency'],
                    equipment_id
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ ML predictions stored for {len(equipment_ids)} equipment")
            return True
            
        except Exception as e:
            print(f"❌ Error storing ML predictions: {str(e)}")
            return False
    
    def _convert_to_time_prediction(self, failure_probability, health_score):
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

# Global model instance
realistic_ml_model = RealisticPredictiveMaintenanceModel()
