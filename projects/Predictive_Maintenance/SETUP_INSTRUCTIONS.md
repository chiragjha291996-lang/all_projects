# Predictive Maintenance - Source Code

## 🚀 Quick Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip (Python package manager)
- npm (Node package manager)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend will run on: http://localhost:5001

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will run on: http://localhost:3001

## 📁 Project Structure

### Backend (`/backend`)
- `app.py` - Main Flask application with API endpoints
- `enhanced_simulator.py` - IoT sensor data simulator with anomaly injection
- `realistic_ml_model.py` - ML training and prediction system
- `sensor_thresholds.py` - Centralized sensor threshold management
- `requirements.txt` - Python dependencies
- `models/` - Pre-trained ML models and scalers

### Frontend (`/frontend`)
- `src/` - React application source code
  - `pages/` - Main application pages (Dashboard, Equipment Detail, Alerts, Analytics)
  - `components/` - Reusable React components
  - `services/` - API service layer
- `package.json` - Node.js dependencies
- Configuration files for Vite, TailwindCSS, PostCSS

## 🎯 Key Features

- **Real-time Dashboard**: Updates every second with live sensor data
- **ML-powered Predictions**: Failure prediction with confidence levels
- **Consistent Thresholds**: Uniform sensor thresholds across all equipment
- **Anomaly Injection**: Simulated equipment failures for testing
- **Professional UI**: Modern React interface with TailwindCSS
- **Comprehensive API**: RESTful endpoints for all functionality

## 🔧 API Endpoints

- `GET /api/dashboard` - Dashboard data
- `GET /api/equipment/:id` - Equipment details
- `GET /api/alerts` - Alert management
- `POST /api/ml/train` - Train ML models
- `POST /api/ml/predict-all` - Generate ML predictions
- `GET /api/thresholds` - Sensor thresholds

## 📊 ML Models

- **Health Score Model**: RandomForest Regressor for equipment health
- **Failure Probability Model**: RandomForest Classifier for failure prediction
- **Feature Engineering**: Derived features from sensor data
- **Incremental Learning**: Models can be retrained with new data

---

**Ready to run!** Extract the zip file and follow the setup instructions above.
