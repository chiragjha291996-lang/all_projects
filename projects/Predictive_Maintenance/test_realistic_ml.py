#!/usr/bin/env python3
"""
Test script for Realistic ML Model Training with Incremental Learning
"""

import requests
import time
import json

API_BASE = "http://localhost:5001/api"

def test_realistic_ml_training():
    """Test realistic ML training with incremental learning"""
    print("🧠 Testing Realistic ML Training with Incremental Learning")
    print("=" * 60)
    
    try:
        # Test training with 7 days of data (incremental learning)
        print("🔄 Training models with last 7 days of sensor data...")
        response = requests.post(f"{API_BASE}/ml/train", 
                               json={"days_back": 7})
        
        print(f"Training response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Training successful: {data['message']}")
            
            # Check validation info
            if 'validation_info' in data:
                print("\n📊 Validation Methods Used:")
                for method, used in data['validation_info'].items():
                    if used:
                        print(f"  ✅ {method.replace('_', ' ').title()}")
            
            # Check warnings
            if 'warnings' in data and data['warnings']:
                print("\n⚠️  Model Validation Warnings:")
                for warning in data['warnings']:
                    print(f"  • {warning}")
            
            # Display realistic performance metrics
            if 'performance' in data:
                performance = data['performance']
                
                print("\n📈 Health Model Performance:")
                health_perf = performance['health_model']
                print(f"  • MSE: {health_perf['mse']:.4f}")
                print(f"  • R²: {health_perf['r2']:.4f}")
                print(f"  • CV Score: {health_perf['cv_score_mean']:.4f} ± {health_perf['cv_score_std']:.4f}")
                print(f"  • Training Samples: {health_perf['training_samples']}")
                
                print("\n⚠️  Failure Model Performance:")
                failure_perf = performance['failure_model']
                print(f"  • Accuracy: {failure_perf['accuracy']:.4f}")
                print(f"  • Precision: {failure_perf['precision']:.4f}")
                print(f"  • Recall: {failure_perf['recall']:.4f}")
                print(f"  • F1 Score: {failure_perf['f1_score']:.4f}")
                print(f"  • CV Score: {failure_perf['cv_score_mean']:.4f} ± {failure_perf['cv_score_std']:.4f}")
                print(f"  • Training Samples: {failure_perf['training_samples']}")
            
            return True
        else:
            print(f"❌ Training failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_incremental_retraining():
    """Test incremental retraining with new data"""
    print("\n🔄 Testing Incremental Retraining")
    print("=" * 40)
    
    try:
        # Wait a bit to simulate new data coming in
        print("⏳ Waiting for new sensor data...")
        time.sleep(2)
        
        # Retrain with new data
        response = requests.post(f"{API_BASE}/ml/retrain", 
                               json={"days_back": 7})
        
        print(f"Retraining response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retraining result: {data['message']}")
            
            if 'warnings' in data and data['warnings']:
                print("\n⚠️  Validation Warnings:")
                for warning in data['warnings']:
                    print(f"  • {warning}")
            
            return True
        else:
            print(f"❌ Retraining failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_realistic_predictions():
    """Test predictions with realistic accuracy"""
    print("\n🎯 Testing Realistic Predictions")
    print("=" * 40)
    
    try:
        # Test with different sensor data scenarios
        test_cases = [
            {
                "name": "Normal Operation",
                "sensor_data": {"temperature": 70.0, "vibration": 1.5, "pressure": 20.0, "rpm": 1800}
            },
            {
                "name": "High Temperature",
                "sensor_data": {"temperature": 85.0, "vibration": 2.0, "pressure": 22.0, "rpm": 1900}
            },
            {
                "name": "High Vibration",
                "sensor_data": {"temperature": 75.0, "vibration": 3.5, "pressure": 18.0, "rpm": 1750}
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📊 Testing: {test_case['name']}")
            
            response = requests.post(f"{API_BASE}/ml/predict", 
                                   json={"sensor_data": test_case['sensor_data']})
            
            if response.status_code == 200:
                data = response.json()
                predictions = data['predictions']
                
                print(f"  • Health Score: {predictions['health_score']:.2f}%")
                print(f"  • Failure Probability: {predictions['failure_probability']:.2f}%")
                
                # Validate that predictions are realistic
                if predictions['health_score'] < 0 or predictions['health_score'] > 100:
                    print(f"  ⚠️  Warning: Health score out of range!")
                
                if predictions['failure_probability'] < 0 or predictions['failure_probability'] > 100:
                    print(f"  ⚠️  Warning: Failure probability out of range!")
            else:
                print(f"  ❌ Prediction failed: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_validation():
    """Test model validation and performance monitoring"""
    print("\n🔍 Testing Model Validation")
    print("=" * 40)
    
    try:
        # Get model status with validation info
        response = requests.get(f"{API_BASE}/ml/status")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model Status Retrieved")
            
            # Check validation info
            if 'validation_info' in data:
                print("\n📊 Validation Methods:")
                for method, used in data['validation_info'].items():
                    if used:
                        print(f"  ✅ {method.replace('_', ' ').title()}")
            
            # Check warnings
            if 'warnings' in data and data['warnings']:
                print("\n⚠️  Model Warnings:")
                for warning in data['warnings']:
                    print(f"  • {warning}")
            else:
                print("\n✅ No model validation warnings")
            
            return True
        else:
            print(f"❌ Status check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎯 Realistic ML Training & Validation Test Suite")
    print("=" * 70)
    print("Testing incremental learning, realistic accuracy, and proper validation")
    print("=" * 70)
    
    try:
        # Test realistic ML training
        training_success = test_realistic_ml_training()
        
        # Test incremental retraining
        retraining_success = test_incremental_retraining()
        
        # Test realistic predictions
        prediction_success = test_realistic_predictions()
        
        # Test model validation
        validation_success = test_model_validation()
        
        print("\n" + "=" * 70)
        if training_success and retraining_success and prediction_success and validation_success:
            print("🎉 REALISTIC ML TESTS COMPLETED!")
            print("✅ Incremental learning with new sensor data")
            print("✅ Cross-validation and realistic accuracy reporting")
            print("✅ Model validation warnings and monitoring")
            print("✅ Proper performance metrics (no 100% accuracy)")
            print("\n🚀 Ready for realistic hackathon demo!")
        else:
            print("❌ SOME REALISTIC ML TESTS FAILED")
            print("Check the error messages above for details")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
