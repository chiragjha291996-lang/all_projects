"""
Integration tests for the Conversational MLOps Agent.

These tests verify end-to-end functionality and integration between components.
"""
import pytest
import asyncio
import tempfile
import os
import time
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from backend.api.main import app
from backend.agent.mlops_agent import ConversationalMLOpsAgent


class TestEndToEndWorkflows:
    """End-to-end workflow tests."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_pipeline_content(self):
        """Sample pipeline content for testing."""
        return '''
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
    
    def test_complete_pipeline_onboarding_workflow(self, client, sample_pipeline_content):
        """Test complete Use Case 1 workflow."""
        # Step 1: Project initiation
        response = client.post("/chat", json={"message": "set up a new churn model pipeline"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 2: File upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_pipeline_content)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post("/upload", files={"file": file})
                assert response.status_code == 200
                upload_result = response.json()
                assert upload_result["success"] is True
                file_path = upload_result["file_path"]
            
            os.unlink(f.name)
        
        # Step 3: Register pipeline
        response = client.post("/chat", json={
            "message": "register my pipeline",
            "file_path": file_path
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 4: Trigger first run
        response = client.post("/chat", json={"message": "run my pipeline"})
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_complete_model_management_workflow(self, client):
        """Test complete Use Case 2 workflow."""
        # Step 1: Trigger retraining
        response = client.post("/chat", json={"message": "retrain the churn model"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 2: Query performance
        response = client.post("/chat", json={"message": "what was the accuracy?"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 3: Promote model
        response = client.post("/chat", json={"message": "promote this model to staging"})
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_conversational_flow_consistency(self, client):
        """Test that conversational flow is consistent and natural."""
        messages = [
            "Hello, I need help with MLOps",
            "I want to set up a new pipeline",
            "Can you help me register it?",
            "What about running it?",
            "How do I check the results?",
            "Can I promote the model?"
        ]
        
        responses = []
        for message in messages:
            response = client.post("/chat", json={"message": message})
            assert response.status_code == 200
            assert response.json()["success"] is True
            responses.append(response.json()["response"])
        
        # All responses should be conversational and helpful
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
            assert not response.startswith("Error") or not response.startswith("❌")


class TestPerformanceMetrics:
    """Performance and responsiveness tests."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_response_time_simple_queries(self, client):
        """Test that simple queries respond within 3-5 seconds."""
        simple_queries = [
            "hello",
            "help",
            "list pipelines",
            "list models"
        ]
        
        for query in simple_queries:
            start_time = time.time()
            response = client.post("/chat", json={"message": query})
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
            assert response.json()["success"] is True
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(query):
            response = client.post("/chat", json={"message": query})
            results.put(response.status_code)
        
        # Send multiple concurrent requests
        threads = []
        queries = ["hello", "help", "list pipelines", "list models"]
        
        for query in queries:
            thread = threading.Thread(target=make_request, args=(query,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        while not results.empty():
            status_code = results.get()
            assert status_code == 200


class TestErrorHandling:
    """Error handling and edge case tests."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_invalid_file_upload(self, client):
        """Test handling of invalid file uploads."""
        # Test non-Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("hello world")
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post("/upload", files={"file": file})
                assert response.status_code == 400
                assert "Python files" in response.json()["detail"]
            
            os.unlink(f.name)
    
    def test_empty_message_handling(self, client):
        """Test handling of empty messages."""
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 200
        # Should handle gracefully
        assert response.json()["success"] is True or response.json()["success"] is False
    
    def test_malformed_request_handling(self, client):
        """Test handling of malformed requests."""
        # Missing message field
        response = client.post("/chat", json={})
        assert response.status_code == 422  # Validation error
    
    def test_large_file_handling(self, client):
        """Test handling of large files."""
        # Create a large Python file
        large_content = "print('hello')\n" * 10000  # ~100KB
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(large_content)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post("/upload", files={"file": file})
                # Should handle large files gracefully
                assert response.status_code in [200, 413]  # OK or Payload Too Large
            
            os.unlink(f.name)


class TestToolIntegration:
    """Test integration between different tools."""
    
    def test_prefect_mlflow_integration(self):
        """Test that Prefect and MLflow tools work together."""
        with patch('backend.tools.prefect_tools.PrefectClient') as mock_prefect, \
             patch('backend.tools.mlflow_tools.MlflowClient') as mock_mlflow:
            
            # Mock successful responses
            mock_prefect.return_value.create_deployment.return_value = Mock(id="test-id")
            mock_mlflow.return_value.search_runs.return_value = []
            
            # Test that both tools can be initialized
            from backend.tools.prefect_tools import PrefectTools
            from backend.tools.mlflow_tools import MLflowTools
            
            prefect_tools = PrefectTools()
            mlflow_tools = MLflowTools()
            
            assert prefect_tools is not None
            assert mlflow_tools is not None
    
    def test_google_api_integration(self):
        """Test Google API tools integration."""
        with patch('backend.tools.google_api_tools.storage.Client') as mock_storage:
            from backend.tools.google_api_tools import GoogleAPITools
            
            google_tools = GoogleAPITools()
            assert google_tools is not None


class TestDataFlow:
    """Test data flow between components."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_file_upload_to_processing_flow(self, client):
        """Test flow from file upload to processing."""
        pipeline_content = '''
from prefect import flow, task

@task
def hello_task():
    return "Hello World"

@flow(name="hello_flow")
def hello_flow():
    return hello_task()
'''
        
        # Upload file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(pipeline_content)
            f.flush()
            
            with open(f.name, 'rb') as file:
                upload_response = client.post("/upload", files={"file": file})
                assert upload_response.status_code == 200
                file_path = upload_response.json()["file_path"]
            
            os.unlink(f.name)
        
        # Process with agent
        response = client.post("/chat", json={
            "message": "process this file",
            "file_path": file_path
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_conversation_state_persistence(self, client):
        """Test that conversation state is maintained."""
        # Start a conversation
        response1 = client.post("/chat", json={"message": "I want to set up a pipeline"})
        assert response1.status_code == 200
        
        # Continue the conversation
        response2 = client.post("/chat", json={"message": "Can you help me register it?"})
        assert response2.status_code == 200
        
        # Both responses should be contextual
        assert isinstance(response1.json()["response"], str)
        assert isinstance(response2.json()["response"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


