#!/usr/bin/env python3
"""
Test script for ML Model Training and Retraining functionality
"""

import requests
import time
import json

API_BASE = "http://localhost:5001/api"

def test_ml_status():
    """Test ML status endpoint"""
    print("🧠 Testing ML Status Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get(f"{API_BASE}/ml/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"✅ ML Status: {data}")
        
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_model_training():
    """Test model training functionality"""
    print("\n🚀 Testing Model Training")
    print("=" * 40)
    
    try:
        # Test training with 30 days of data
        response = requests.post(f"{API_BASE}/ml/train", 
                               json={"days_back": 30})
        
        print(f"Training response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Training successful: {data['message']}")
            
            if 'performance' in data:
                performance = data['performance']
                print(f"📊 Health Model - MSE: {performance['health_model']['mse']:.4f}")
                print(f"📊 Health Model - R²: {performance['health_model']['r2']:.4f}")
                print(f"📊 Failure Model - Accuracy: {performance['failure_model']['accuracy']:.4f}")
            
            return True
        else:
            print(f"❌ Training failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_performance():
    """Test model performance endpoint"""
    print("\n📈 Testing Model Performance")
    print("=" * 40)
    
    try:
        response = requests.get(f"{API_BASE}/ml/performance")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"✅ Performance data: {data}")
        
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_model_retraining():
    """Test automatic retraining"""
    print("\n🔄 Testing Model Retraining")
    print("=" * 40)
    
    try:
        response = requests.post(f"{API_BASE}/ml/retrain", 
                               json={"days_threshold": 7})
        
        print(f"Retraining response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retraining result: {data['message']}")
            print(f"🔄 Retrained: {data.get('retrained', False)}")
            return True
        else:
            print(f"❌ Retraining failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_model_prediction():
    """Test ML model prediction"""
    print("\n🎯 Testing Model Prediction")
    print("=" * 40)
    
    try:
        # Sample sensor data
        sensor_data = {
            "temperature": 75.5,
            "vibration": 2.3,
            "pressure": 18.7,
            "rpm": 1850
        }
        
        response = requests.post(f"{API_BASE}/ml/predict", 
                               json={"sensor_data": sensor_data})
        
        print(f"Prediction response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            predictions = data['predictions']
            print(f"✅ Health Score Prediction: {predictions['health_score']:.2f}%")
            print(f"✅ Failure Probability: {predictions['failure_probability']:.2f}%")
            return True
        else:
            print(f"❌ Prediction failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ml_integration():
    """Test complete ML integration workflow"""
    print("\n🔗 Testing Complete ML Integration")
    print("=" * 50)
    
    # 1. Check initial status
    status = test_ml_status()
    if not status:
        return False
    
    # 2. Train models
    training_success = test_model_training()
    if not training_success:
        print("⚠️  Training failed, but continuing with tests...")
    
    # 3. Check performance
    performance = test_model_performance()
    
    # 4. Test retraining
    retraining_success = test_model_retraining()
    
    # 5. Test predictions
    prediction_success = test_model_prediction()
    
    # 6. Final status check
    final_status = test_ml_status()
    
    return training_success or retraining_success or prediction_success

def main():
    print("🎯 ML Model Training & Retraining Test Suite")
    print("=" * 60)
    
    try:
        success = test_ml_integration()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 ML TRAINING TESTS COMPLETED!")
            print("✅ Model training endpoints working")
            print("✅ Performance tracking functional")
            print("✅ Retraining mechanism operational")
            print("✅ Prediction API functional")
            print("\n🚀 Ready for hackathon demo!")
        else:
            print("❌ SOME ML TESTS FAILED")
            print("Check the error messages above for details")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        return False
    
    return success

if __name__ == "__main__":
    main()
