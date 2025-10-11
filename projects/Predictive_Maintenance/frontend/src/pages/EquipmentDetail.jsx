import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { dashboardAPI } from '../services/api';
import { ArrowLeft, AlertTriangle, CheckCircle, Clock, Settings, Play, Pause, Wrench } from 'lucide-react';

const EquipmentDetail = () => {
  const { id } = useParams();
  const [equipmentData, setEquipmentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState({});

  const fetchEquipmentData = async () => {
    try {
      const response = await dashboardAPI.getEquipmentDetail(id);
      setEquipmentData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch equipment data');
      console.error('Equipment API error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEquipmentData();
    
    // Set up real-time updates every 1 second
    const interval = setInterval(fetchEquipmentData, 1000);
    
    return () => clearInterval(interval);
  }, [id]);

  const handleManualAction = async (action) => {
    setActionLoading(prev => ({ ...prev, [action]: true }));
    
    // Simulate API call for manual action
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log(`Executing ${action} for equipment ${id}`);
      
      // Show success message (in a real app, this would be a toast notification)
      alert(`${action} executed successfully!`);
    } catch (err) {
      alert(`Failed to execute ${action}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [action]: false }));
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-6 w-6 text-health-green" />;
      case 'warning':
        return <AlertTriangle className="h-6 w-6 text-health-yellow" />;
      case 'critical':
        return <AlertTriangle className="h-6 w-6 text-health-red" />;
      default:
        return <Clock className="h-6 w-6 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-health-green';
      case 'warning':
        return 'bg-health-yellow';
      case 'critical':
        return 'bg-health-red';
      default:
        return 'bg-gray-400';
    }
  };

  const formatSensorData = (sensorData) => {
    if (!sensorData) return [];
    
    return Object.entries(sensorData).map(([sensorType, data]) => ({
      sensorType,
      data: data.slice(0, 20).map(item => ({
        time: new Date(item.timestamp).toLocaleTimeString(),
        value: item.value,
        thresholdMin: item.threshold_min,
        thresholdMax: item.threshold_max
      }))
    }));
  };

  const getFailureProbabilityColor = (probability) => {
    if (probability >= 70) return '#EF4444'; // red (critical threshold)
    if (probability >= 50) return '#F59E0B'; // yellow (warning threshold)
    return '#10B981'; // green (normal)
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!equipmentData) {
    return (
      <div className="text-center py-8">
        <h2 className="text-xl font-semibold text-gray-900">Equipment not found</h2>
        <Link to="/" className="text-blue-600 hover:text-blue-800">← Back to Dashboard</Link>
      </div>
    );
  }

  const { equipment, sensorData, alerts } = equipmentData;
  const formattedSensorData = formatSensorData(sensorData);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link 
            to="/" 
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5" />
            <span>Back to Dashboard</span>
          </Link>
          <div className="h-6 w-px bg-gray-300"></div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{equipment.name}</h1>
            <p className="text-gray-600">{equipment.type}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {getStatusIcon(equipment.status)}
          <div className="text-right">
            <p className="text-sm font-medium text-gray-700">{equipment.status}</p>
            <p className="text-xs text-gray-500">Health: {equipment.healthScore}%</p>
            <p className="text-xs text-green-600 animate-pulse">● Live</p>
          </div>
        </div>
      </div>

      {/* Equipment Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Health Score */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Health Score</h3>
            <div className={`w-4 h-4 rounded-full ${getStatusColor(equipment.status)}`}></div>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            {equipment.healthScore}%
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${getStatusColor(equipment.status)}`}
              style={{ width: `${equipment.healthScore}%` }}
            ></div>
          </div>
        </div>

        {/* Failure Prediction */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Failure Prediction</h3>
          <div className={`text-2xl font-bold mb-2 ${
            equipment.predictionUrgency === 'IMMEDIATE' ? 'text-red-600' :
            equipment.predictionUrgency === 'URGENT' ? 'text-red-600' :
            equipment.predictionUrgency === 'SCHEDULE' ? 'text-yellow-600' :
            equipment.predictionUrgency === 'MONITOR' ? 'text-yellow-600' : 'text-green-600'
          }`}>
            {equipment.failurePrediction}
          </div>
          <div className="text-sm text-gray-600 mb-1">
            Confidence: {equipment.predictionConfidence}
          </div>
          <div className="text-sm text-gray-500">
            Urgency: {equipment.predictionUrgency}
          </div>
        </div>

        {/* Manual Actions */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button
              onClick={() => handleManualAction('restart')}
              disabled={actionLoading.restart}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {actionLoading.restart ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Play className="h-4 w-4" />
              )}
              <span>Restart Equipment</span>
            </button>
            
            <button
              onClick={() => handleManualAction('reduce_load')}
              disabled={actionLoading.reduce_load}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {actionLoading.reduce_load ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Pause className="h-4 w-4" />
              )}
              <span>Reduce Load</span>
            </button>
            
            <button
              onClick={() => handleManualAction('schedule_maintenance')}
              disabled={actionLoading.schedule_maintenance}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {actionLoading.schedule_maintenance ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Wrench className="h-4 w-4" />
              )}
              <span>Schedule Maintenance</span>
            </button>
          </div>
        </div>
      </div>

      {/* Sensor Charts */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Sensor Readings (Last Hour) • Live Updates</h3>
        
        {formattedSensorData.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {formattedSensorData.map(({ sensorType, data }) => (
              <div key={sensorType} className="space-y-4">
                <h4 className="text-md font-medium text-gray-700 capitalize">
                  {sensorType.replace('_', ' ')}
                </h4>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="time" 
                        tick={{ fontSize: 12 }}
                        interval="preserveStartEnd"
                      />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'value') return [value, 'Current Value'];
                          if (name === 'thresholdMax') return [value, 'Warning Threshold (High)'];
                          if (name === 'thresholdMin') return [value, 'Warning Threshold (Low)'];
                          return [value, name];
                        }}
                        labelFormatter={(label) => `Time: ${label}`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#3B82F6" 
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        name="Current Value"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="thresholdMax" 
                        stroke="#F59E0B" 
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                        name="Warning Threshold (High)"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="thresholdMin" 
                        stroke="#F59E0B" 
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                        name="Warning Threshold (Low)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Clock className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No sensor data available yet</p>
            <p className="text-sm">Data will appear as the simulator generates readings</p>
          </div>
        )}
      </div>

      {/* Recent Alerts */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Alerts</h3>
        
        {alerts && alerts.length > 0 ? (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <AlertTriangle className={`h-5 w-5 ${
                    alert.severity === 'critical' ? 'text-red-500' : 
                    alert.severity === 'warning' ? 'text-yellow-500' : 'text-blue-500'
                  }`} />
                  <div>
                    <p className="font-medium text-gray-900">
                      {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)} Alert
                    </p>
                    <p className="text-sm text-gray-600">
                      Triggered by: {alert.sensorTrigger} • 
                      Failure Probability: {alert.failureProbability}%
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    {new Date(alert.createdAt).toLocaleString()}
                  </p>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    alert.status === 'active' ? 'bg-red-100 text-red-800' :
                    alert.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {alert.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-400" />
            <p>No recent alerts</p>
            <p className="text-sm">Equipment is operating normally</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EquipmentDetail;
