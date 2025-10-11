import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { AlertCircle, TrendingUp, Clock, CheckCircle } from 'lucide-react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    try {
      const response = await dashboardAPI.getDashboardData();
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard API error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Set up real-time updates every 1 second
    const interval = setInterval(fetchDashboardData, 1000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (statusColor) => {
    switch (statusColor) {
      case 'green':
        return 'bg-health-green';
      case 'yellow':
        return 'bg-health-yellow';
      case 'red':
        return 'bg-health-red';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-health-green" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-health-yellow" />;
      case 'critical':
        return <AlertCircle className="h-5 w-5 text-health-red" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
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
          <AlertCircle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Real-time monitoring of industrial equipment health
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          <span>Live updates every second • Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* System Metrics */}
      {dashboardData?.metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertCircle className="h-8 w-8 text-red-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Alerts</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.metrics.activeAlerts}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Resolved Alerts</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.metrics.resolvedAlerts}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Uptime</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.metrics.uptimePercentage}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-purple-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Predictions Today</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.metrics.predictionsToday}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Equipment Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {dashboardData?.equipment?.map((equipment) => (
          <Link
            key={equipment.id}
            to={`/equipment/${equipment.id}`}
            className="block bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {equipment.name}
                  </h3>
                  <p className="text-sm text-gray-500">{equipment.type}</p>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(equipment.status)}
                  <span className="text-sm font-medium text-gray-700">
                    {equipment.status}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Health Score</span>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(equipment.statusColor)}`}></div>
                    <span className="text-sm font-semibold text-gray-900">
                      {equipment.healthScore}%
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-sm text-gray-500">Failure Prediction</span>
                  <div className={`text-sm font-semibold ${
                    equipment.predictionUrgency === 'IMMEDIATE' ? 'text-red-600' :
                    equipment.predictionUrgency === 'URGENT' ? 'text-red-600' :
                    equipment.predictionUrgency === 'SCHEDULE' ? 'text-yellow-600' :
                    equipment.predictionUrgency === 'MONITOR' ? 'text-yellow-600' : 'text-green-600'
                  }`}>
                    {equipment.failurePrediction}
                  </div>
                  <div className="text-xs text-gray-500">
                    Confidence: {equipment.predictionConfidence}
                  </div>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getStatusColor(equipment.statusColor)}`}
                    style={{ width: `${equipment.healthScore}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Alert Badge */}
      {dashboardData?.metrics?.activeAlerts > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                {dashboardData.metrics.activeAlerts} Active Alert{dashboardData.metrics.activeAlerts > 1 ? 's' : ''}
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <Link to="/alerts" className="font-medium underline">
                  View alerts →
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
