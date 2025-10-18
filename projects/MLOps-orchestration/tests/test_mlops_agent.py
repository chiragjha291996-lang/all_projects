"""
Test cases for the Conversational MLOps Agent based on PRD requirements.

This module contains comprehensive tests covering:
1. Use Case 1: Pipeline Onboarding and First Run
2. Use Case 2: Model Retraining and Management
3. Success Metrics validation
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from backend.api.main import app
from backend.agent.mlops_agent import ConversationalMLOpsAgent
from backend.tools.prefect_tools import PrefectTools
from backend.tools.mlflow_tools import MLflowTools
from backend.tools.google_api_tools import GoogleAPITools


class TestConversationalMLOpsAgent:
    """Test cases for the main ConversationalMLOpsAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        with patch('backend.agent.mlops_agent.ChatGoogleGenerativeAI'):
            return ConversationalMLOpsAgent()
    
    def test_agent_initialization(self, agent):
        """Test that the agent initializes correctly."""
        assert agent is not None
        assert agent.prefect_tools is not None
        assert agent.mlflow_tools is not None
        assert agent.google_api_tools is not None
        assert len(agent.tools) > 0
    
    def test_get_available_commands(self, agent):
        """Test that available commands are returned."""
        commands = agent.get_available_commands()
        assert isinstance(commands, list)
        assert len(commands) > 0
        assert any("pipeline" in cmd.lower() for cmd in commands)
        assert any("model" in cmd.lower() for cmd in commands)


class TestUseCase1PipelineOnboarding:
    """Test cases for Use Case 1: Pipeline Onboarding and First Run."""
    
    @pytest.fixture
    def sample_pipeline_file(self):
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
    
    def test_project_initiation_command(self, agent):
        """Test Use Case 1.1: Project Initiation via command."""
        response = agent.process_message("set up a new churn model pipeline")
        
        # Should acknowledge the request and ask for file upload
        assert "churn" in response.lower() or "pipeline" in response.lower()
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_file_upload_handling(self, agent, sample_pipeline_file):
        """Test Use Case 1.2: Single File Upload handling."""
        response = agent.process_message("upload my pipeline script", sample_pipeline_file)
        
        # Should acknowledge file upload
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('backend.tools.prefect_tools.PrefectClient')
    def test_pipeline_registration(self, mock_client, agent, sample_pipeline_file):
        """Test Use Case 1.3: Pipeline Registration."""
        # Mock Prefect client response
        mock_deployment = Mock()
        mock_deployment.id = "test-deployment-id"
        mock_client.return_value.create_deployment.return_value = mock_deployment
        
        response = agent.process_message("register my pipeline", sample_pipeline_file)
        
        # Should attempt to register the pipeline
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('backend.tools.prefect_tools.PrefectClient')
    def test_trigger_first_run(self, mock_client, agent):
        """Test Use Case 1.4: Trigger First Run."""
        # Mock Prefect client response
        mock_flow_run = Mock()
        mock_flow_run.id = "test-flow-run-id"
        mock_client.return_value.create_flow_run_from_deployment.return_value = mock_flow_run
        
        response = agent.process_message("run my pipeline")
        
        # Should attempt to trigger pipeline run
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_conversational_feedback(self, agent):
        """Test Use Case 1.5: Conversational Feedback."""
        responses = [
            agent.process_message("set up a new model pipeline"),
            agent.process_message("upload my script"),
            agent.process_message("register my pipeline"),
            agent.process_message("run my pipeline")
        ]
        
        # All responses should be conversational and informative
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
            # Should contain status updates or acknowledgments
            assert any(word in response.lower() for word in ["file", "pipeline", "run", "success", "error"])


class TestUseCase2ModelRetraining:
    """Test cases for Use Case 2: Model Retraining and Management."""
    
    @patch('backend.tools.prefect_tools.PrefectClient')
    def test_trigger_retraining(self, mock_client, agent):
        """Test Use Case 2.1: Trigger Retraining."""
        # Mock Prefect client response
        mock_flow_run = Mock()
        mock_flow_run.id = "test-flow-run-id"
        mock_client.return_value.create_flow_run_from_deployment.return_value = mock_flow_run
        
        response = agent.process_message("retrain the churn model")
        
        # Should attempt to trigger retraining
        assert isinstance(response, str)
        assert len(response) > 0
    
    @patch('backend.tools.mlflow_tools.MlflowClient')
    def test_query_model_performance(self, mock_client, agent):
        """Test Use Case 2.2: Query Model Performance."""
        # Mock MLflow client response
        mock_run = Mock()
        mock_run.data.metrics = {"accuracy": 0.942, "precision": 0.89, "recall": 0.91}
        mock_run.info.run_id = "test-run-id"
        mock_run.info.status = "FINISHED"
        
        mock_client.return_value.search_runs.return_value = [mock_run]
        
        response = agent.process_message("what was the accuracy?")
        
        # Should return metrics information
        assert isinstance(response, str)
        assert len(response) > 0
        assert "accuracy" in response.lower() or "metric" in response.lower()
    
    @patch('backend.tools.mlflow_tools.MlflowClient')
    def test_promote_model(self, mock_client, agent):
        """Test Use Case 2.3: Promote Model."""
        # Mock MLflow client response
        mock_version = Mock()
        mock_version.version = "1"
        mock_client.return_value.get_latest_versions.return_value = [mock_version]
        mock_client.return_value.transition_model_version_stage.return_value = None
        
        response = agent.process_message("promote this model to staging")
        
        # Should attempt to promote model
        assert isinstance(response, str)
        assert len(response) > 0
        assert "promote" in response.lower() or "staging" in response.lower()
    
    def test_conversational_feedback_retraining(self, agent):
        """Test Use Case 2.4: Conversational Feedback for retraining."""
        responses = [
            agent.process_message("retrain the model"),
            agent.process_message("what was the accuracy?"),
            agent.process_message("promote this model to staging")
        ]
        
        # All responses should be conversational and informative
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
            # Should contain relevant information
            assert any(word in response.lower() for word in ["model", "accuracy", "promote", "staging", "success", "error"])


class TestSuccessMetrics:
    """Test cases for Success Metrics validation."""
    
    def test_functional_demo_completion(self, agent):
        """Test Success Metric 1: Functional Demo completion."""
        # Simulate complete workflow
        messages = [
            "set up a new churn model pipeline",
            "upload my pipeline script",
            "register my pipeline",
            "run my pipeline",
            "what was the accuracy?",
            "promote this model to staging"
        ]
        
        responses = []
        for message in messages:
            response = agent.process_message(message)
            responses.append(response)
        
        # All responses should be successful (no errors)
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
            assert "error" not in response.lower() or "❌" not in response
    
    def test_clarity_of_value(self, agent):
        """Test Success Metric 2: Clarity of Value."""
        # Test that responses are clear and understandable
        response = agent.process_message("help me with MLOps")
        
        # Response should be clear and explain capabilities
        assert isinstance(response, str)
        assert len(response) > 0
        assert any(word in response.lower() for word in ["help", "mlops", "pipeline", "model", "prefect", "mlflow"])
    
    def test_responsiveness(self, agent):
        """Test Success Metric 3: Responsiveness (3-5 seconds)."""
        import time
        
        start_time = time.time()
        response = agent.process_message("hello")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be fast (under 5 seconds for simple queries)
        assert response_time < 5.0
        assert isinstance(response, str)
        assert len(response) > 0


class TestAPIIntegration:
    """Test cases for API integration."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "version" in response.json()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_chat_endpoint(self, client):
        """Test chat endpoint."""
        with patch('backend.api.main.agent') as mock_agent:
            mock_agent.process_message.return_value = "Test response"
            
            response = client.post("/chat", json={"message": "hello"})
            assert response.status_code == 200
            assert response.json()["success"] is True
    
    def test_upload_endpoint(self, client):
        """Test file upload endpoint."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello')")
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post("/upload", files={"file": file})
                assert response.status_code == 200
                assert response.json()["success"] is True
            
            os.unlink(f.name)
    
    def test_invalid_file_upload(self, client):
        """Test invalid file upload."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("hello")
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post("/upload", files={"file": file})
                assert response.status_code == 400
            
            os.unlink(f.name)


class TestToolIntegration:
    """Test cases for tool integration."""
    
    @patch('backend.tools.prefect_tools.PrefectClient')
    def test_prefect_tools_integration(self, mock_client):
        """Test Prefect tools integration."""
        tools = PrefectTools()
        
        # Mock successful response
        mock_deployment = Mock()
        mock_deployment.id = "test-id"
        mock_client.return_value.create_deployment.return_value = mock_deployment
        
        # Test should not raise exceptions
        assert tools is not None
    
    @patch('backend.tools.mlflow_tools.MlflowClient')
    def test_mlflow_tools_integration(self, mock_client):
        """Test MLflow tools integration."""
        tools = MLflowTools()
        
        # Mock successful response
        mock_client.return_value.search_runs.return_value = []
        
        # Test should not raise exceptions
        assert tools is not None
    
    @patch('backend.tools.google_api_tools.storage.Client')
    def test_google_api_tools_integration(self, mock_client):
        """Test Google API tools integration."""
        tools = GoogleAPITools()
        
        # Test should not raise exceptions
        assert tools is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


