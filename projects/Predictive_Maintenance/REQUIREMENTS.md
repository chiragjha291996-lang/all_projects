# Predictive Maintenance System - Requirements Document

## Project Overview
A real-time predictive maintenance system that monitors 3 industrial equipment units (Pump, Compressor, Conveyor Belt) using 4 sensors each (Temperature, Vibration, Pressure, RPM). The system predicts equipment failures, sends automated alerts, and triggers remediation workflows to prevent downtime.

## User Stories

**US-1**: As an operations manager, I want to view real-time health status of all equipment on a single dashboard so I can quickly identify at-risk assets.

**US-2**: As a maintenance technician, I want to see detailed sensor readings and failure predictions for specific equipment so I can plan preventive maintenance.

**US-3**: As a reliability engineer, I want to receive automated alerts when failure probability exceeds thresholds so I can take action before equipment fails.

**US-4**: As a plant manager, I want to review model performance metrics and cost savings so I can justify the predictive maintenance investment.

---

## Screen Specifications

### Screen 1: Dashboard (Home)
**Purpose**: Centralized monitoring of all equipment health and system status.

**Components**:
- Equipment grid displaying 3 cards (Pump, Compressor, Conveyor Belt)
- Each card shows: equipment name, current health score (0-100%), failure probability, status indicator (healthy/warning/critical)
- Summary metrics: total alerts (active/resolved), uptime percentage, predictions made today
- Real-time data refresh every 5 seconds

**Acceptance Criteria**:
- AC-1.1: Health scores update automatically without page refresh
- AC-1.2: Status color codes: Green (0-40%), Yellow (41-79%), Red (80-100%)
- AC-1.3: Clicking equipment card navigates to Equipment Detail screen
- AC-1.4: Alert count badge visible when active alerts exist

---

### Screen 2: Equipment Detail
**Purpose**: Deep-dive monitoring of individual equipment with sensor telemetry and prediction timeline.

**Components**:
- Equipment header with name, current status, and failure probability gauge
- 4 live sensor charts (line graphs): Temperature (°C), Vibration (mm/s), Pressure (PSI), RPM
- Each chart displays last 60 minutes of data with threshold lines
- Prediction panel showing failure probability for next 24 hours
- Manual action buttons: "Restart Equipment", "Reduce Load", "Schedule Maintenance"
- Recent alerts history for this equipment (last 10)

**Acceptance Criteria**:
- AC-2.1: Sensor charts update in real-time with smooth animations
- AC-2.2: Threshold violations highlighted in red on charts
- AC-2.3: Manual action buttons trigger remediation workflows and display confirmation
- AC-2.4: Failure probability gauge shows percentage with color coding

---

### Screen 3: Alerts & Workflows
**Purpose**: Manage alerts and monitor automated remediation workflow execution.

**Components**:
- Alert list table with columns: timestamp, equipment, severity, failure probability, sensor trigger, status (active/acknowledged/resolved)
- Filter controls: equipment type, severity level, date range
- Alert detail panel showing sensor readings at alert trigger time
- Workflow execution log with columns: workflow ID, type (restart/reduce load/maintenance), equipment, status (pending/running/completed/failed), timestamp
- Acknowledge/Dismiss buttons for active alerts

**Acceptance Criteria**:
- AC-3.1: Alerts sorted by timestamp (newest first)
- AC-3.2: Severity badges: Critical (red), Warning (yellow), Info (blue)
- AC-3.3: Acknowledging alert updates status and logs action
- AC-3.4: Workflow status updates automatically; failed workflows highlighted
- AC-3.5: Search/filter returns results within 1 second

---

### Screen 4: Analytics & Model Performance
**Purpose**: Monitor ML model effectiveness and demonstrate business value.

**Components**:
- Model metrics cards: Accuracy (%), Precision (%), Recall (%), F1 Score
- Prediction performance chart: True positives, false positives, false negatives over time
- Business impact metrics: Prevented failures count, estimated cost savings ($), system uptime (%)
- Model information: version, training date, records used, feature importance bar chart
- Manual retrain button with last retrain timestamp

**Acceptance Criteria**:
- AC-4.1: Metrics displayed with percentage values and trend indicators (↑↓)
- AC-4.2: Cost savings calculated as: prevented failures × $25,000 per failure
- AC-4.3: Feature importance shows top 4 sensors contributing to predictions
- AC-4.4: Retrain button triggers model retraining and updates metrics within 30 seconds
- AC-4.5: Performance chart displays data for last 7 days

---

## Technical Requirements
- **Backend**: Flask REST API, SQLite database, scikit-learn Random Forest model
- **Frontend**: React with Vite, TailwindCSS, Recharts library
- **Data**: 3 equipment × 4 sensors, data points every 5 seconds
- **Alerts**: Email/SMS simulation (logged and displayed in UI)
- **Performance**: API response time < 200ms, UI load time < 2 seconds

## Non-Functional Requirements
- Input validation on all API endpoints
- Error handling with user-friendly messages
- Responsive design (desktop optimized)
- Automated unit tests (backend) and component tests (frontend)
- Comprehensive documentation including prompt library

