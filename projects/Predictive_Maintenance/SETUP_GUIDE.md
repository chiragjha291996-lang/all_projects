# Predictive Maintenance System - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python3 app.py
```
Backend runs on: http://localhost:5001

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on: http://localhost:3001

## 📁 Project Structure
```
Predictive_Maintenance/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── enhanced_simulator.py # IoT data simulator
│   ├── realistic_ml_model.py # ML models
│   ├── requirements.txt    # Python dependencies
│   └── predictive_maintenance.db # SQLite database
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Dashboard, Equipment, Alerts, Analytics
│   │   └── services/      # API client
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Build configuration
└── REQUIREMENTS.md        # Project requirements
```

## 🎯 Features
- **Real-time Dashboard**: Equipment monitoring with ML predictions
- **Equipment Details**: Individual equipment analysis
- **Alert Management**: Alert filtering and resolution
- **ML Analytics**: Model training, retraining, and performance metrics
- **IoT Simulation**: Realistic sensor data with anomaly injection

## 🔧 Key APIs
- `GET /api/dashboard` - Equipment status and metrics
- `GET /api/equipment/:id` - Equipment details
- `GET /api/alerts` - Alert management
- `POST /api/ml/train` - Train ML models
- `POST /api/ml/predict-all` - Generate ML predictions

## 📊 Demo Data
The system includes:
- 3 equipment (Pump, Compressor, Conveyor)
- 4 sensor types (Temperature, Vibration, Pressure, RPM)
- ML models for health score and failure prediction
- Anomaly injection for realistic testing

## 🎉 Ready for Hackathon Demo!
