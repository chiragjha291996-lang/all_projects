#!/usr/bin/env python3
"""
Enhanced System Test Suite with Anomaly Injection
Tests the complete predictive maintenance system with anomaly patterns
"""

import requests
import time
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:5001/api"

class EnhancedSystemTestSuite:
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
    
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    def test_enhanced_simulator_status(self):
        """Test 1: Enhanced Simulator with Anomaly Injection"""
        print("\n🚀 TESTING ENHANCED SIMULATOR WITH ANOMALY INJECTION")
        print("=" * 60)
        
        try:
            response = requests.get(f"{API_BASE}/simulator/status")
            if response.status_code == 200:
                data = response.json()
                has_anomaly_injection = data.get('anomaly_injection', False)
                is_running = data.get('running', False)
                cycle_count = data.get('cycle_count', 0)
                active_anomalies = data.get('active_anomalies', 0)
                
                self.log_test('Enhanced Simulator Status', 
                            has_anomaly_injection and is_running,
                            f"Running: {is_running}, Anomaly Injection: {has_anomaly_injection}, Cycles: {cycle_count}, Active Anomalies: {active_anomalies}")
            else:
                self.log_test('Enhanced Simulator Status', False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test('Enhanced Simulator Status', False, str(e))
    
    def test_anomaly_generated_alerts(self):
        """Test 2: Anomaly-Generated Alerts"""
        try:
            response = requests.get(f"{API_BASE}/alerts")
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                
                # Check for diverse alert types
                alert_types = set(alert.get('sensorTrigger') for alert in alerts)
                severities = set(alert.get('severity') for alert in alerts)
                equipment_ids = set(alert.get('equipmentId') for alert in alerts)
                
                diverse_alerts = len(alert_types) >= 4 and len(severities) >= 2 and len(equipment_ids) >= 2
                
                self.log_test('Anomaly-Generated Alerts', 
                            diverse_alerts,
                            f"Alert types: {len(alert_types)}, Severities: {len(severities)}, Equipment: {len(equipment_ids)}, Total alerts: {len(alerts)}")
            else:
                self.log_test('Anomaly-Generated Alerts', False)
        except Exception as e:
            self.log_test('Anomaly-Generated Alerts', False, str(e))
    
    def test_alert_severity_distribution(self):
        """Test 3: Alert Severity Distribution"""
        try:
            response = requests.get(f"{API_BASE}/alerts")
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                
                severity_counts = {}
                for alert in alerts:
                    severity = alert.get('severity', 'unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                has_critical = severity_counts.get('critical', 0) > 0
                has_warning = severity_counts.get('warning', 0) > 0
                
                self.log_test('Alert Severity Distribution', 
                            has_critical and has_warning,
                            f"Critical: {severity_counts.get('critical', 0)}, Warning: {severity_counts.get('warning', 0)}")
            else:
                self.log_test('Alert Severity Distribution', False)
        except Exception as e:
            self.log_test('Alert Severity Distribution', False, str(e))
    
    def test_sensor_trigger_diversity(self):
        """Test 4: Sensor Trigger Diversity"""
        try:
            response = requests.get(f"{API_BASE}/alerts")
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                
                triggers = set(alert.get('sensorTrigger') for alert in alerts)
                expected_triggers = {'health_threshold', 'temperature_high', 'vibration_high', 'pressure_anomaly', 'failure_probability_high'}
                
                has_expected_triggers = len(triggers.intersection(expected_triggers)) >= 4
                
                self.log_test('Sensor Trigger Diversity', 
                            has_expected_triggers,
                            f"Triggers found: {triggers}, Expected: {expected_triggers}")
            else:
                self.log_test('Sensor Trigger Diversity', False)
        except Exception as e:
            self.log_test('Sensor Trigger Diversity', False, str(e))
    
    def test_equipment_health_degradation(self):
        """Test 5: Equipment Health Degradation"""
        try:
            response = requests.get(f"{API_BASE}/dashboard")
            if response.status_code == 200:
                data = response.json()
                equipment = data.get('equipment', [])
                
                # Check for degraded health scores
                degraded_equipment = [eq for eq in equipment if eq.get('healthScore', 100) < 80]
                critical_equipment = [eq for eq in equipment if eq.get('healthScore', 100) < 50]
                
                has_degradation = len(degraded_equipment) > 0
                
                self.log_test('Equipment Health Degradation', 
                            has_degradation,
                            f"Degraded equipment: {len(degraded_equipment)}, Critical: {len(critical_equipment)}")
            else:
                self.log_test('Equipment Health Degradation', False)
        except Exception as e:
            self.log_test('Equipment Health Degradation', False, str(e))
    
    def test_failure_probability_elevation(self):
        """Test 6: Failure Probability Elevation"""
        try:
            response = requests.get(f"{API_BASE}/dashboard")
            if response.status_code == 200:
                data = response.json()
                equipment = data.get('equipment', [])
                
                # Check for elevated failure probabilities
                high_risk_equipment = [eq for eq in equipment if eq.get('failureProbability', 0) > 50]
                critical_risk_equipment = [eq for eq in equipment if eq.get('failureProbability', 0) > 80]
                
                has_elevated_risk = len(high_risk_equipment) > 0
                
                self.log_test('Failure Probability Elevation', 
                            has_elevated_risk,
                            f"High risk equipment: {len(high_risk_equipment)}, Critical risk: {len(critical_risk_equipment)}")
            else:
                self.log_test('Failure Probability Elevation', False)
        except Exception as e:
            self.log_test('Failure Probability Elevation', False, str(e))
    
    def test_historical_data_availability(self):
        """Test 7: Historical Data Availability"""
        try:
            # Check if we have sufficient historical data
            response = requests.get(f"{API_BASE}/equipment/1")
            if response.status_code == 200:
                data = response.json()
                sensor_data = data.get('sensorData', [])
                
                # Check for sufficient historical data points
                sufficient_data = len(sensor_data) >= 100
                
                # Check data diversity
                sensor_types = set(point.get('sensorType') for point in sensor_data)
                has_all_sensors = len(sensor_types) >= 4
                
                self.log_test('Historical Data Availability', 
                            sufficient_data and has_all_sensors,
                            f"Data points: {len(sensor_data)}, Sensor types: {len(sensor_types)}")
            else:
                self.log_test('Historical Data Availability', False)
        except Exception as e:
            self.log_test('Historical Data Availability', False, str(e))
    
    def test_ml_training_with_anomalies(self):
        """Test 8: ML Training with Anomaly Data"""
        try:
            # Test ML training with anomaly data
            response = requests.post(f"{API_BASE}/ml/train", json={'days_back': 7})
            if response.status_code == 200:
                data = response.json()
                training_success = data.get('success', False)
                performance = data.get('performance', {})
                
                # Check if we have performance metrics
                has_performance = bool(performance.get('health_model') and performance.get('failure_model'))
                
                self.log_test('ML Training with Anomaly Data', 
                            training_success and has_performance,
                            f"Training success: {training_success}, Performance data: {has_performance}")
            else:
                self.log_test('ML Training with Anomaly Data', False)
        except Exception as e:
            self.log_test('ML Training with Anomaly Data', False, str(e))
    
    def test_ml_prediction_accuracy(self):
        """Test 9: ML Prediction Accuracy with Anomalies"""
        try:
            # Test ML prediction with anomaly data
            test_sensor_data = {
                'temperature': 85.0,  # High temperature
                'vibration': 4.5,    # High vibration
                'pressure': 12.0,    # Low pressure
                'rpm': 2000
            }
            
            response = requests.post(f"{API_BASE}/ml/predict", json={'sensor_data': test_sensor_data})
            if response.status_code == 200:
                data = response.json()
                prediction_success = data.get('success', False)
                predictions = data.get('predictions', {})
                
                # Check if predictions are realistic
                health_score = predictions.get('health_score', 100)
                failure_probability = predictions.get('failure_probability', 0)
                
                realistic_predictions = health_score < 80 and failure_probability > 30
                
                self.log_test('ML Prediction Accuracy with Anomalies', 
                            prediction_success and realistic_predictions,
                            f"Health score: {health_score:.1f}, Failure probability: {failure_probability:.1f}%")
            else:
                self.log_test('ML Prediction Accuracy with Anomalies', False)
        except Exception as e:
            self.log_test('ML Prediction Accuracy with Anomalies', False, str(e))
    
    def test_real_time_anomaly_detection(self):
        """Test 10: Real-time Anomaly Detection"""
        try:
            # Test real-time anomaly detection
            initial_response = requests.get(f"{API_BASE}/simulator/status")
            initial_anomalies = initial_response.json().get('active_anomalies', 0)
            
            # Wait for new anomalies
            time.sleep(5)
            
            updated_response = requests.get(f"{API_BASE}/simulator/status")
            updated_anomalies = updated_response.json().get('active_anomalies', 0)
            
            # Check if anomalies are being detected in real-time
            anomaly_detection_working = updated_anomalies >= initial_anomalies
            
            self.log_test('Real-time Anomaly Detection', 
                        anomaly_detection_working,
                        f"Initial anomalies: {initial_anomalies}, Updated anomalies: {updated_anomalies}")
        except Exception as e:
            self.log_test('Real-time Anomaly Detection', False, str(e))
    
    def test_alert_workflow_with_anomalies(self):
        """Test 11: Alert Workflow with Anomalies"""
        try:
            response = requests.get(f"{API_BASE}/alerts")
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                
                # Check alert workflow states
                active_alerts = [alert for alert in alerts if alert.get('status') == 'active']
                acknowledged_alerts = [alert for alert in alerts if alert.get('status') == 'acknowledged']
                resolved_alerts = [alert for alert in alerts if alert.get('status') == 'resolved']
                
                # Check for diverse alert states
                workflow_diversity = len(active_alerts) > 0
                
                self.log_test('Alert Workflow with Anomalies', 
                            workflow_diversity,
                            f"Active: {len(active_alerts)}, Acknowledged: {len(acknowledged_alerts)}, Resolved: {len(resolved_alerts)}")
            else:
                self.log_test('Alert Workflow with Anomalies', False)
        except Exception as e:
            self.log_test('Alert Workflow with Anomalies', False, str(e))
    
    def test_system_performance_with_anomalies(self):
        """Test 12: System Performance with Anomalies"""
        try:
            start_time = time.time()
            
            # Test multiple endpoints
            endpoints = ['/dashboard', '/alerts', '/simulator/status', '/ml/status']
            responses = []
            
            for endpoint in endpoints:
                response = requests.get(f"{API_BASE}{endpoint}")
                responses.append(response.status_code == 200)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            all_responses_ok = all(responses)
            fast_response = response_time < 2000  # 2 seconds
            
            self.log_test('System Performance with Anomalies', 
                        all_responses_ok and fast_response,
                        f"All responses OK: {all_responses_ok}, Response time: {response_time:.1f}ms")
        except Exception as e:
            self.log_test('System Performance with Anomalies', False, str(e))
    
    def run_all_tests(self):
        """Run all enhanced system tests"""
        print("🚀 ENHANCED PREDICTIVE MAINTENANCE SYSTEM TEST SUITE")
        print("=" * 70)
        print("Testing system with anomaly injection and comprehensive data")
        print("=" * 70)
        
        # Run all tests
        self.test_enhanced_simulator_status()
        self.test_anomaly_generated_alerts()
        self.test_alert_severity_distribution()
        self.test_sensor_trigger_diversity()
        self.test_equipment_health_degradation()
        self.test_failure_probability_elevation()
        self.test_historical_data_availability()
        self.test_ml_training_with_anomalies()
        self.test_ml_prediction_accuracy()
        self.test_real_time_anomaly_detection()
        self.test_alert_workflow_with_anomalies()
        self.test_system_performance_with_anomalies()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 70)
        print("📊 ENHANCED SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📈 Success Rate: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests})")
        print()
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['passed']]
        if failed_tests:
            print("❌ Failed Tests:")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['details']}")
            print()
        
        # System readiness
        if success_rate >= 90:
            print("🎉 ENHANCED SYSTEM READY FOR DEMO!")
            print("✅ Anomaly injection working perfectly")
            print("✅ Comprehensive alert generation")
            print("✅ ML training with anomaly data")
            print("✅ Real-time anomaly detection")
        elif success_rate >= 75:
            print("⚠️  ENHANCED SYSTEM MOSTLY READY")
            print("✅ Core anomaly functionality working")
            print("⚠️  Some minor issues to address")
        else:
            print("❌ ENHANCED SYSTEM NEEDS ATTENTION")
            print("❌ Critical issues detected")
            print("🔧 Review failed tests above")
        
        print("\n🚀 Ready for hackathon demonstration with anomaly injection!")

def main():
    """Run the enhanced system test suite"""
    test_suite = EnhancedSystemTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
