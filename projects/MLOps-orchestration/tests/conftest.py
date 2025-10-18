"""
Pytest configuration and test utilities.
"""
import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables."""
    os.environ.update({
        "PREFECT_API_URL": "http://localhost:4200/api",
        "MLFLOW_TRACKING_URI": "http://localhost:5000",
        "MLFLOW_EXPERIMENT_NAME": "test-experiment",
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "LANGCHAIN_API_KEY": "test-key"
    })


@pytest.fixture
def mock_prefect_client():
    """Mock Prefect client for testing."""
    with patch('backend.tools.prefect_tools.PrefectClient') as mock:
        mock_instance = Mock()
        mock_instance.create_deployment.return_value = Mock(id="test-deployment-id")
        mock_instance.create_flow_run_from_deployment.return_value = Mock(id="test-flow-run-id")
        mock_instance.read_deployments.return_value = []
        mock_instance.read_flow_run.return_value = Mock(state=Mock(type=Mock(value="COMPLETED")))
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_mlflow_client():
    """Mock MLflow client for testing."""
    with patch('backend.tools.mlflow_tools.MlflowClient') as mock:
        mock_instance = Mock()
        mock_run = Mock()
        mock_run.data.metrics = {"accuracy": 0.942, "precision": 0.89}
        mock_run.info.run_id = "test-run-id"
        mock_run.info.status = "FINISHED"
        mock_instance.search_runs.return_value = [mock_run]
        mock_instance.get_run.return_value = mock_run
        mock_instance.search_experiments.return_value = []
        mock_instance.get_latest_versions.return_value = [Mock(version="1")]
        mock_instance.transition_model_version_stage.return_value = None
        mock_instance.search_registered_models.return_value = []
        mock_instance.get_registered_model.return_value = Mock(description="Test model")
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_google_storage_client():
    """Mock Google Storage client for testing."""
    with patch('backend.tools.google_api_tools.storage.Client') as mock:
        mock_instance = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_instance.bucket.return_value = mock_bucket
        mock_instance.list_buckets.return_value = []
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_pipeline_file():
    """Create a sample pipeline file for testing."""
    content = '''
from prefect import flow, task
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

@task
def load_data():
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    return X, y

@task
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    return model, X_test, y_test

@task
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    with mlflow.start_run():
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(model, "test_model")
    
    return accuracy

@flow(name="test_pipeline")
def test_pipeline():
    X, y = load_data()
    model, X_test, y_test = train_model(X, y)
    accuracy = evaluate_model(model, X_test, y_test)
    return accuracy
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        f.flush()
        yield f.name
    
    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def agent():
    """Create a test agent instance."""
    with patch('backend.agent.mlops_agent.ChatGoogleGenerativeAI'):
        from backend.agent.mlops_agent import ConversationalMLOpsAgent
        return ConversationalMLOpsAgent()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Mark unit tests
        elif "test_" in item.nodeid and "integration" not in item.nodeid:
            item.add_marker(pytest.mark.unit)
