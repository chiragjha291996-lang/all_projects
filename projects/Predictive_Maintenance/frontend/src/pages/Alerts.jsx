import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Filter, 
  Search, 
  RefreshCw, 
  Eye, 
  XCircle,
  Bell,
  TrendingUp,
  Activity,
  Zap
} from 'lucide-react';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [equipmentFilter, setEquipmentFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Statistics
  const [alertStats, setAlertStats] = useState({
    total: 0,
    active: 0,
    acknowledged: 0,
    resolved: 0,
    critical: 0,
    warning: 0
  });

  const fetchAlerts = async () => {
    try {
      setError(null);
      const response = await api.get('/alerts');
      const alertsData = response.data.alerts || [];
      setAlerts(alertsData);
      
      // Calculate statistics
      const stats = {
        total: alertsData.length,
        active: alertsData.filter(alert => alert.status === 'active').length,
        acknowledged: alertsData.filter(alert => alert.status === 'acknowledged').length,
        resolved: alertsData.filter(alert => alert.status === 'resolved').length,
        critical: alertsData.filter(alert => alert.severity === 'critical').length,
        warning: alertsData.filter(alert => alert.severity === 'warning').length
      };
      setAlertStats(stats);
      
    } catch (err) {
      setError('Failed to fetch alerts');
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    // Set up real-time updates every 2 seconds
    const interval = setInterval(fetchAlerts, 2000);
    
    return () => clearInterval(interval);
  }, []);

  // Filter alerts based on current filters
  useEffect(() => {
    let filtered = alerts;

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(alert => alert.status === statusFilter);
    }

    // Severity filter
    if (severityFilter !== 'all') {
      filtered = filtered.filter(alert => alert.severity === severityFilter);
    }

    // Equipment filter
    if (equipmentFilter !== 'all') {
      filtered = filtered.filter(alert => alert.equipmentId.toString() === equipmentFilter);
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(alert => 
        alert.equipmentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.sensorTrigger.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.id.toString().includes(searchTerm)
      );
    }

    setFilteredAlerts(filtered);
  }, [alerts, statusFilter, severityFilter, equipmentFilter, searchTerm]);

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      // Simulate acknowledge action (would be a real API call)
      setAlerts(prevAlerts => 
        prevAlerts.map(alert => 
          alert.id === alertId 
            ? { ...alert, status: 'acknowledged', acknowledgedAt: new Date().toISOString() }
            : alert
        )
      );
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      // Simulate resolve action (would be a real API call)
      setAlerts(prevAlerts => 
        prevAlerts.map(alert => 
          alert.id === alertId 
            ? { ...alert, status: 'resolved', resolvedAt: new Date().toISOString() }
            : alert
        )
      );
    } catch (err) {
      console.error('Error resolving alert:', err);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-red-600 bg-red-100';
      case 'acknowledged': return 'text-yellow-600 bg-yellow-100';
      case 'resolved': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <AlertTriangle className="h-4 w-4" />;
      case 'acknowledged': return <Clock className="h-4 w-4" />;
      case 'resolved': return <CheckCircle className="h-4 w-4" />;
      default: return <Bell className="h-4 w-4" />;
    }
  };

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown';
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now - alertTime;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const getUniqueEquipment = () => {
    const equipment = [...new Set(alerts.map(alert => ({ id: alert.equipmentId, name: alert.equipmentName })))];
    return equipment;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading alerts...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts & Workflows</h1>
          <p className="mt-2 text-gray-600">Monitor and manage equipment alerts in real-time</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Activity className="h-4 w-4" />
          <span>Live updates every 2 seconds • Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}

      {/* Alert Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Bell className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Alerts</p>
              <p className="text-2xl font-bold text-gray-900">{alertStats.total}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Active</p>
              <p className="text-2xl font-bold text-red-600">{alertStats.active}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Acknowledged</p>
              <p className="text-2xl font-bold text-yellow-600">{alertStats.acknowledged}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Resolved</p>
              <p className="text-2xl font-bold text-green-600">{alertStats.resolved}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <XCircle className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Critical</p>
              <p className="text-2xl font-bold text-red-600">{alertStats.critical}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Warning</p>
              <p className="text-2xl font-bold text-yellow-600">{alertStats.warning}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center space-x-4 mb-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search alerts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>
          
          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Severity</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
          
          {/* Equipment Filter */}
          <select
            value={equipmentFilter}
            onChange={(e) => setEquipmentFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Equipment</option>
            {getUniqueEquipment().map(equipment => (
              <option key={equipment.id} value={equipment.id}>
                {equipment.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Alerts ({filteredAlerts.length})
          </h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredAlerts.length === 0 ? (
            <div className="p-8 text-center">
              <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No alerts found</h3>
              <p className="text-gray-500">
                {alerts.length === 0 
                  ? "No alerts have been generated yet." 
                  : "No alerts match your current filters."}
              </p>
            </div>
          ) : (
            filteredAlerts.map((alert) => (
              <div key={alert.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {/* Status Icon */}
                    <div className={`p-2 rounded-full ${getStatusColor(alert.status)}`}>
                      {getStatusIcon(alert.status)}
                    </div>
                    
                    {/* Alert Info */}
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-medium text-gray-900">
                          {alert.equipmentName}
                        </h4>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getSeverityColor(alert.severity)}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(alert.status)}`}>
                          {alert.status.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <p><strong>Trigger:</strong> {alert.sensorTrigger.replace('_', ' ').toUpperCase()}</p>
                        <p><strong>Failure Probability:</strong> {alert.failureProbability.toFixed(1)}%</p>
                        <p><strong>Created:</strong> {formatTimeAgo(alert.createdAt)}</p>
                        {alert.acknowledgedAt && (
                          <p><strong>Acknowledged:</strong> {formatTimeAgo(alert.acknowledgedAt)}</p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        setSelectedAlert(alert);
                        setShowDetails(true);
                      }}
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      title="View Details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    
                    {alert.status === 'active' && (
                      <>
                        <button
                          onClick={() => handleAcknowledgeAlert(alert.id)}
                          className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200 transition-colors"
                        >
                          Acknowledge
                        </button>
                        <button
                          onClick={() => handleResolveAlert(alert.id)}
                          className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200 transition-colors"
                        >
                          Resolve
                        </button>
                      </>
                    )}
                    
                    {alert.status === 'acknowledged' && (
                      <button
                        onClick={() => handleResolveAlert(alert.id)}
                        className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200 transition-colors"
                      >
                        Resolve
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Alert Details Modal */}
      {showDetails && selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Alert Details</h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Equipment</label>
                  <p className="text-lg font-semibold text-gray-900">{selectedAlert.equipmentName}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Alert ID</label>
                  <p className="text-lg font-semibold text-gray-900">#{selectedAlert.id}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Severity</label>
                  <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full border ${getSeverityColor(selectedAlert.severity)}`}>
                    {selectedAlert.severity.toUpperCase()}
                  </span>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(selectedAlert.status)}`}>
                    {selectedAlert.status.toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Sensor Trigger</label>
                <p className="text-gray-900">{selectedAlert.sensorTrigger.replace('_', ' ').toUpperCase()}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Failure Probability</label>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        selectedAlert.failureProbability >= 70 ? 'bg-red-500' :
                        selectedAlert.failureProbability >= 50 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${selectedAlert.failureProbability}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {selectedAlert.failureProbability.toFixed(1)}%
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Created</label>
                  <p className="text-gray-900">{new Date(selectedAlert.createdAt).toLocaleString()}</p>
                </div>
                {selectedAlert.acknowledgedAt && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Acknowledged</label>
                    <p className="text-gray-900">{new Date(selectedAlert.acknowledgedAt).toLocaleString()}</p>
                  </div>
                )}
              </div>
              
              {/* Recommended Actions */}
              <div className="border-t pt-4">
                <h4 className="text-md font-semibold text-gray-900 mb-3">Recommended Actions</h4>
                <div className="space-y-2">
                  {selectedAlert.severity === 'critical' && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-800">
                        <strong>Immediate Action Required:</strong> Equipment requires immediate attention. 
                        Consider shutting down and scheduling emergency maintenance.
                      </p>
                    </div>
                  )}
                  {selectedAlert.severity === 'warning' && (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                      <p className="text-sm text-yellow-800">
                        <strong>Schedule Maintenance:</strong> Equipment shows signs of degradation. 
                        Schedule preventive maintenance within 24-48 hours.
                      </p>
                    </div>
                  )}
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <p className="text-sm text-blue-800">
                      <strong>Monitor Closely:</strong> Continue monitoring sensor readings and 
                      equipment performance for any further changes.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setShowDetails(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                Close
              </button>
              {selectedAlert.status === 'active' && (
                <>
                  <button
                    onClick={() => {
                      handleAcknowledgeAlert(selectedAlert.id);
                      setShowDetails(false);
                    }}
                    className="px-4 py-2 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-md hover:bg-yellow-200 transition-colors"
                  >
                    Acknowledge
                  </button>
                  <button
                    onClick={() => {
                      handleResolveAlert(selectedAlert.id);
                      setShowDetails(false);
                    }}
                    className="px-4 py-2 text-sm font-medium text-green-800 bg-green-100 rounded-md hover:bg-green-200 transition-colors"
                  >
                    Resolve
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;