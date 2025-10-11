import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { 
  Brain, TrendingUp, AlertTriangle, RefreshCw, 
  Play, Pause, Activity, Target, Zap
} from 'lucide-react';
import api from '../services/api';

const Analytics = () => {
  const [mlStatus, setMlStatus] = useState(null);
  const [modelPerformance, setModelPerformance] = useState(null);
  const [trainingStatus, setTrainingStatus] = useState('idle'); // idle, training, completed, error
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [retrainingEnabled, setRetrainingEnabled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [thresholds, setThresholds] = useState(null);

  // Mock analytics data
  const mockData = {
    modelAccuracy: [
      { name: 'Health Model', accuracy: 87.5, color: '#10B981' },
      { name: 'Failure Model', accuracy: 92.3, color: '#3B82F6' },
      { name: 'Alert Model', accuracy: 89.1, color: '#F59E0B' }
    ],
    trainingHistory: [
      { date: '2024-01-01', accuracy: 85.2, samples: 1000 },
      { date: '2024-01-02', accuracy: 86.8, samples: 1200 },
      { date: '2024-01-03', accuracy: 87.5, samples: 1400 },
      { date: '2024-01-04', accuracy: 88.1, samples: 1600 },
      { date: '2024-01-05', accuracy: 89.3, samples: 1800 },
      { date: '2024-01-06', accuracy: 90.7, samples: 2000 },
      { date: '2024-01-07', accuracy: 92.3, samples: 2200 }
    ],
    predictionAccuracy: [
      { hour: '00:00', accuracy: 89.2 },
      { hour: '04:00', accuracy: 91.5 },
      { hour: '08:00', accuracy: 88.7 },
      { hour: '12:00', accuracy: 93.1 },
      { hour: '16:00', accuracy: 90.8 },
      { hour: '20:00', accuracy: 87.9 }
    ]
  };

  useEffect(() => {
    fetchMLStatus();
    fetchModelPerformance();
    fetchThresholds();
    
    // Set up auto-refresh every 5 seconds
    const interval = setInterval(() => {
      fetchMLStatus();
      fetchModelPerformance();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchMLStatus = async () => {
    try {
      const response = await api.get('/ml/status');
      setMlStatus(response.data);
    } catch (error) {
      console.error('Error fetching ML status:', error);
    }
  };

  const fetchModelPerformance = async () => {
    try {
      const response = await api.get('/ml/performance');
      setModelPerformance(response.data);
    } catch (error) {
      console.error('Error fetching model performance:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchThresholds = async () => {
    try {
      const response = await api.get('/thresholds');
      setThresholds(response.data.thresholds);
    } catch (error) {
      console.error('Error fetching thresholds:', error);
    }
  };

  const trainModels = async (daysBack = 7) => {
    setTrainingStatus('training');
    setTrainingProgress(0);
    
    try {
      // Simulate training progress
      const progressInterval = setInterval(() => {
        setTrainingProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 15;
        });
      }, 500);

      const response = await api.post('/ml/train', { days_back: daysBack });
      
      clearInterval(progressInterval);
      setTrainingProgress(100);
      
      if (response.data.success) {
        setTrainingStatus('completed');
        setModelPerformance(response.data);
        
        // Reset status after 3 seconds
        setTimeout(() => {
          setTrainingStatus('idle');
          setTrainingProgress(0);
        }, 3000);
      } else {
        setTrainingStatus('error');
      }
    } catch (error) {
      console.error('Error training models:', error);
      setTrainingStatus('error');
    }
  };

  const retrainModels = async () => {
    setTrainingStatus('training');
    setTrainingProgress(0);
    
    try {
      const response = await api.post('/ml/retrain');
      
      if (response.data.success) {
        setTrainingStatus('completed');
        if (response.data.retrained) {
          setModelPerformance(response.data);
        }
        
        setTimeout(() => {
          setTrainingStatus('idle');
          setTrainingProgress(0);
        }, 3000);
      } else {
        setTrainingStatus('error');
      }
    } catch (error) {
      console.error('Error retraining models:', error);
      setTrainingStatus('error');
    }
  };

  const generateMLPredictions = async () => {
    setTrainingStatus('training');
    
    try {
      const response = await api.post('/ml/predict-all');
      
      if (response.data.success) {
        setTrainingStatus('completed');
        
        // Reset status after 2 seconds
        setTimeout(() => {
          setTrainingStatus('idle');
        }, 2000);
      } else {
        setTrainingStatus('error');
      }
    } catch (error) {
      console.error('Error generating ML predictions:', error);
      setTrainingStatus('error');
    }
  };

  const toggleAutoRetraining = () => {
    setRetrainingEnabled(!retrainingEnabled);
    // In a real implementation, this would configure automatic retraining
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-2 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics & Model Performance</h1>
          <p className="mt-2 text-gray-600">
            Monitor ML model performance and manage training processes
          </p>
        </div>

        {/* ML Model Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Model Training Status */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Model Status</h3>
              <Brain className="h-6 w-6 text-blue-600" />
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Models Trained:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  mlStatus?.models_trained ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {mlStatus?.models_trained ? 'Yes' : 'No'}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Needs Retraining:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  mlStatus?.needs_retraining ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                }`}>
                  {mlStatus?.needs_retraining ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>

          {/* Training Controls */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Training Controls</h3>
              <Activity className="h-6 w-6 text-green-600" />
            </div>
            
            <div className="space-y-3">
              <button
                onClick={() => trainModels(30)}
                disabled={trainingStatus === 'training'}
                className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
                  trainingStatus === 'training'
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {trainingStatus === 'training' ? (
                  <div className="flex items-center justify-center">
                    <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                    Training...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Play className="h-4 w-4 mr-2" />
                    Train Models (7 days)
                  </div>
                )}
              </button>
              
              <button
                onClick={retrainModels}
                disabled={trainingStatus === 'training'}
                className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
                  trainingStatus === 'training'
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                <div className="flex items-center justify-center">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retrain with New Data
                </div>
              </button>
              
              <button
                onClick={generateMLPredictions}
                disabled={trainingStatus === 'training'}
                className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
                  trainingStatus === 'training'
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                <div className="flex items-center justify-center">
                  <Brain className="h-4 w-4 mr-2" />
                  Generate ML Predictions
                </div>
              </button>
            </div>
          </div>

          {/* Auto Retraining */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Auto Retraining</h3>
              <Zap className="h-6 w-6 text-yellow-600" />
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Enabled:</span>
                <button
                  onClick={toggleAutoRetraining}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    retrainingEnabled ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      retrainingEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              
              <p className="text-xs text-gray-500">
                Automatically retrain models every 7 days
              </p>
            </div>
          </div>
        </div>

        {/* Training Progress */}
        {trainingStatus === 'training' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Training Progress</h3>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${trainingProgress}%` }}
              />
            </div>
            <p className="mt-2 text-sm text-gray-600">
              Training ML models... {Math.round(trainingProgress)}%
            </p>
          </div>
        )}

        {/* Model Performance Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Model Accuracy */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Model Accuracy</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockData.modelAccuracy}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="accuracy" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Training History */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Training History</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockData.trainingHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="accuracy" stroke="#10B981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Metrics */}
        {modelPerformance?.performance && (
          <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Current Model Performance</h3>
            
            {/* Warnings Section */}
            {modelPerformance.warnings && modelPerformance.warnings.length > 0 && (
              <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-medium text-yellow-800 mb-2">⚠️ Model Validation Warnings</h4>
                <ul className="text-sm text-yellow-700 space-y-1">
                  {modelPerformance.warnings.map((warning, index) => (
                    <li key={index}>• {warning}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Validation Info */}
            {modelPerformance.validation_info && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-medium text-green-800 mb-2">✅ Validation Methods Used</h4>
                <div className="text-sm text-green-700 space-y-1">
                  {modelPerformance.validation_info.cross_validation_used && (
                    <div>• Cross-validation with 5 folds</div>
                  )}
                  {modelPerformance.validation_info.realistic_accuracy && (
                    <div>• Realistic accuracy reporting (no overfitting)</div>
                  )}
                  {modelPerformance.validation_info.incremental_learning && (
                    <div>• Incremental learning with new sensor data</div>
                  )}
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Health Model Performance */}
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Health Score Prediction Model</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Mean Squared Error:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.health_model?.mse?.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">R² Score:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.health_model?.r2?.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">CV Score (Mean ± Std):</span>
                    <span className="font-medium text-sm">
                      {modelPerformance.performance.health_model?.cv_score_mean?.toFixed(4) || 'N/A'}
                      {modelPerformance.performance.health_model?.cv_score_std && 
                        ` ± ${modelPerformance.performance.health_model.cv_score_std.toFixed(4)}`}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Training Samples:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.health_model?.training_samples || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last Trained:</span>
                    <span className="font-medium text-sm">
                      {modelPerformance.performance.health_model?.last_trained ? 
                        new Date(modelPerformance.performance.health_model.last_trained).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Failure Model Performance */}
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Failure Probability Model</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Accuracy:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.failure_model?.accuracy?.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Precision:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.failure_model?.precision?.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Recall:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.failure_model?.recall?.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">F1 Score:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.failure_model?.f1_score?.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">CV Score (Mean ± Std):</span>
                    <span className="font-medium text-sm">
                      {modelPerformance.performance.failure_model?.cv_score_mean?.toFixed(4) || 'N/A'}
                      {modelPerformance.performance.failure_model?.cv_score_std && 
                        ` ± ${modelPerformance.performance.failure_model.cv_score_std.toFixed(4)}`}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Training Samples:</span>
                    <span className="font-medium">
                      {modelPerformance.performance.failure_model?.training_samples || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Sensor Thresholds */}
        {thresholds && (
          <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">📊 Consistent Sensor Thresholds</h3>
            <p className="text-sm text-gray-600 mb-6">
              Standardized thresholds applied across all equipment types for consistent alerting
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Temperature Thresholds */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-3">🌡️ Temperature (°C)</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-blue-700">Critical High:</span>
                    <span className="font-medium text-red-600">{thresholds.temperature.critical_high}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Warning High:</span>
                    <span className="font-medium text-yellow-600">{thresholds.temperature.warning_high}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Normal Range:</span>
                    <span className="font-medium text-green-600">{thresholds.temperature.normal_min}-{thresholds.temperature.normal_max}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Warning Low:</span>
                    <span className="font-medium text-yellow-600">{thresholds.temperature.warning_low}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Critical Low:</span>
                    <span className="font-medium text-red-600">{thresholds.temperature.critical_low}°C</span>
                  </div>
                </div>
              </div>

              {/* Vibration Thresholds */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-green-900 mb-3">📳 Vibration (mm/s)</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-green-700">Critical High:</span>
                    <span className="font-medium text-red-600">{thresholds.vibration.critical_high} mm/s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">Warning High:</span>
                    <span className="font-medium text-yellow-600">{thresholds.vibration.warning_high} mm/s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">Normal Range:</span>
                    <span className="font-medium text-green-600">{thresholds.vibration.normal_min}-{thresholds.vibration.normal_max} mm/s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">Warning Low:</span>
                    <span className="font-medium text-yellow-600">{thresholds.vibration.warning_low} mm/s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">Critical Low:</span>
                    <span className="font-medium text-red-600">{thresholds.vibration.critical_low} mm/s</span>
                  </div>
                </div>
              </div>

              {/* Pressure Thresholds */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-3">🔧 Pressure (bar)</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-purple-700">Critical High:</span>
                    <span className="font-medium text-red-600">{thresholds.pressure.critical_high} bar</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-700">Warning High:</span>
                    <span className="font-medium text-yellow-600">{thresholds.pressure.warning_high} bar</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-700">Normal Range:</span>
                    <span className="font-medium text-green-600">{thresholds.pressure.normal_min}-{thresholds.pressure.normal_max} bar</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-700">Warning Low:</span>
                    <span className="font-medium text-yellow-600">{thresholds.pressure.warning_low} bar</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-700">Critical Low:</span>
                    <span className="font-medium text-red-600">{thresholds.pressure.critical_low} bar</span>
                  </div>
                </div>
              </div>

              {/* RPM Thresholds */}
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-medium text-orange-900 mb-3">⚙️ RPM</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-orange-700">Critical High:</span>
                    <span className="font-medium text-red-600">{thresholds.rpm.critical_high} RPM</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-700">Warning High:</span>
                    <span className="font-medium text-yellow-600">{thresholds.rpm.warning_high} RPM</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-700">Normal Range:</span>
                    <span className="font-medium text-green-600">{thresholds.rpm.normal_min}-{thresholds.rpm.normal_max} RPM</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-700">Warning Low:</span>
                    <span className="font-medium text-yellow-600">{thresholds.rpm.warning_low} RPM</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-700">Critical Low:</span>
                    <span className="font-medium text-red-600">{thresholds.rpm.critical_low} RPM</span>
                  </div>
                </div>
              </div>

              {/* Health Score Thresholds */}
              <div className="bg-red-50 p-4 rounded-lg">
                <h4 className="font-medium text-red-900 mb-3">❤️ Health Score (%)</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-red-700">Excellent:</span>
                    <span className="font-medium text-green-600">{thresholds.health_score.excellent_min}-{thresholds.health_score.normal_max}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-red-700">Normal:</span>
                    <span className="font-medium text-blue-600">{thresholds.health_score.normal_min}-{thresholds.health_score.excellent_min}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-red-700">Warning:</span>
                    <span className="font-medium text-yellow-600">{thresholds.health_score.warning_low}-{thresholds.health_score.normal_min}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-red-700">Critical:</span>
                    <span className="font-medium text-red-600">0-{thresholds.health_score.critical_low}%</span>
                  </div>
                </div>
              </div>

              {/* Failure Probability Thresholds */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">⚠️ Failure Probability (%)</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-700">Low Risk:</span>
                    <span className="font-medium text-green-600">0-{thresholds.failure_probability.low_max}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-700">Normal:</span>
                    <span className="font-medium text-blue-600">{thresholds.failure_probability.low_max}-{thresholds.failure_probability.normal_max}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-700">Warning:</span>
                    <span className="font-medium text-yellow-600">{thresholds.failure_probability.warning_high}-{thresholds.failure_probability.critical_high}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-700">Critical:</span>
                    <span className="font-medium text-red-600">{thresholds.failure_probability.critical_high}-100%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Prediction Accuracy Over Time */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Prediction Accuracy Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockData.predictionAccuracy}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="accuracy" stroke="#8B5CF6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Analytics;