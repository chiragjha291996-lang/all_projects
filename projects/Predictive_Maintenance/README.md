# Predictive Maintenance System

A real-time predictive maintenance system that monitors industrial equipment using IoT sensor data, predicts failures, and automates alerts and remediation workflows.

## Features

- **Real-time Equipment Monitoring**: Monitor 3 equipment types (Pump, Compressor, Conveyor Belt) with 4 sensors each
- **Predictive Analytics**: ML-powered failure prediction using sensor data patterns
- **Automated Alerting**: Email/SMS alerts when failure probability exceeds thresholds
- **Remediation Workflows**: Automated actions to prevent equipment failures
- **Dashboard**: Real-time visualization of equipment health and system metrics

## Technology Stack

- **Backend**: Flask (Python), SQLite database
- **Frontend**: React, Vite, TailwindCSS, Recharts
- **ML**: scikit-learn Random Forest model
- **IoT Simulation**: Custom Python simulator with realistic sensor data

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:5000` and automatically:
- Initialize the SQLite database
- Seed initial equipment data
- Start the IoT simulator

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:3001`

## API Endpoints

- `GET /api/dashboard` - Get dashboard data (equipment status, metrics)
- `GET /api/equipment/{id}` - Get detailed equipment information
- `GET /api/alerts` - Get alerts with optional filtering
- `POST /api/simulator/start` - Start IoT simulator
- `POST /api/simulator/stop` - Stop IoT simulator
- `GET /api/simulator/status` - Get simulator status

## Screen 1: Dashboard Acceptance Criteria

✅ **AC-1.1**: Health scores update automatically without page refresh (5-second polling)
✅ **AC-1.2**: Status color codes: Green (0-40%), Yellow (41-79%), Red (80-100%)
✅ **AC-1.3**: Clicking equipment card navigates to Equipment Detail screen
✅ **AC-1.4**: Alert count badge visible when active alerts exist

## Demo Scenarios

1. **Normal Operations**: All equipment healthy, low failure probabilities
2. **Anomaly Detection**: Gradual sensor degradation triggers alerts
3. **Auto-Remediation**: Automated workflows prevent failures
4. **Failure Event**: Equipment failure with escalation
5. **Model Performance**: Analytics showing business value

## Development Notes

- IoT simulator generates realistic sensor data every 5 seconds
- Health scores calculated based on sensor threshold proximity
- Failure probability inversely related to health score
- Alerts created when failure probability > 80% or health score < 50%
- Real-time updates via polling (no WebSockets for simplicity)
