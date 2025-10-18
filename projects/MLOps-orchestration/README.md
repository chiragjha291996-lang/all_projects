# Conversational MLOps Agent MVP

A conversational agent that simplifies MLOps workflows by providing a natural language interface to Prefect and MLflow.

## Architecture

- **Backend**: LangGraph agent with Google APIs integration
- **Frontend**: React UI for file upload and chat interface
- **MLOps Stack**: Prefect (orchestration) + MLflow (experiment tracking)

## Project Structure

```
├── backend/                 # LangGraph agent backend
│   ├── agent/              # LangGraph agent implementation
│   ├── tools/              # Prefect and MLflow tools
│   ├── api/                # FastAPI endpoints
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/               # React components
│   └── public/            # Static assets
├── demo/                  # Sample pipeline scripts
├── tests/                 # Integration tests
└── docs/                  # Documentation
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables (see `.env.example`)
3. Start Prefect server: `prefect server start`
4. Start MLflow server: `mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns`
5. Run backend: `python -m backend.main`
6. Run frontend: `cd frontend && npm start`

## Testing

Run tests: `pytest tests/`

## Use Cases

1. **Pipeline Onboarding**: Upload a pipeline script and register it with Prefect
2. **Model Management**: Trigger retraining, check performance, promote models


