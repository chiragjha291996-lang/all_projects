"""
MLflow tools for experiment tracking and model management.
"""
import mlflow
import mlflow.sklearn
import mlflow.tracking
from mlflow.tracking import MlflowClient
from typing import Dict, Any, Optional, List
import pandas as pd


class MLflowTools:
    """Tools for interacting with MLflow for experiment tracking and model management."""
    
    def __init__(self, tracking_uri: str = "http://localhost:5000", experiment_name: str = "conversational-mlops"):
        """Initialize MLflow client."""
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        
        try:
            mlflow.set_tracking_uri(tracking_uri)
            
            # Set or create experiment
            try:
                experiment = mlflow.get_experiment_by_name(experiment_name)
                if experiment is None:
                    experiment_id = mlflow.create_experiment(experiment_name)
                else:
                    experiment_id = experiment.experiment_id
            except Exception:
                experiment_id = mlflow.create_experiment(experiment_name)
            
            self.experiment_id = experiment_id
            self.client = MlflowClient(tracking_uri=tracking_uri)
        except Exception as e:
            # Fallback for testing or when MLflow server is not available
            print(f"Warning: Could not initialize MLflow: {e}")
            self.experiment_id = "test-experiment-id"
            self.client = None
    
    def get_latest_run_metrics(self, experiment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics from the latest run in an experiment.
        
        Args:
            experiment_name: Name of the experiment (defaults to instance experiment)
            
        Returns:
            Dictionary with metrics and run details
        """
        try:
            if self.client is None:
                return {
                    "success": False,
                    "error": "MLflow client not initialized"
                }
            
            exp_name = experiment_name or self.experiment_name
            experiment = mlflow.get_experiment_by_name(exp_name)
            
            if experiment is None:
                return {
                    "success": False,
                    "error": f"Experiment '{exp_name}' not found"
                }
            
            # Get latest run
            runs = self.client.search_runs(
                experiment_ids=[experiment.experiment_id],
                max_results=1,
                order_by=["start_time DESC"]
            )
            
            if not runs:
                return {
                    "success": False,
                    "error": f"No runs found in experiment '{exp_name}'"
                }
            
            latest_run = runs[0]
            metrics = latest_run.data.metrics
            
            return {
                "success": True,
                "experiment_name": exp_name,
                "run_id": latest_run.info.run_id,
                "metrics": metrics,
                "status": latest_run.info.status,
                "message": f"Retrieved metrics from latest run in '{exp_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get latest run metrics: {str(e)}"
            }
    
    def get_run_metrics(self, run_id: str) -> Dict[str, Any]:
        """
        Get metrics from a specific run.
        
        Args:
            run_id: ID of the run
            
        Returns:
            Dictionary with metrics and run details
        """
        try:
            if self.client is None:
                return {
                    "success": False,
                    "error": "MLflow client not initialized"
                }
            
            run = self.client.get_run(run_id)
            metrics = run.data.metrics
            
            return {
                "success": True,
                "run_id": run_id,
                "metrics": metrics,
                "status": run.info.status,
                "message": f"Retrieved metrics from run {run_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get run metrics: {str(e)}"
            }
    
    def list_experiments(self) -> Dict[str, Any]:
        """
        List all experiments.
        
        Returns:
            Dictionary with list of experiments
        """
        try:
            if self.client is None:
                return {
                    "success": False,
                    "error": "MLflow client not initialized"
                }
            
            experiments = self.client.search_experiments()
            
            experiment_list = []
            for exp in experiments:
                experiment_list.append({
                    "name": exp.name,
                    "experiment_id": exp.experiment_id,
                    "lifecycle_stage": exp.lifecycle_stage
                })
            
            return {
                "success": True,
                "experiments": experiment_list,
                "count": len(experiment_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list experiments: {str(e)}"
            }
    
    def promote_model(self, model_name: str, version: Optional[str] = None, stage: str = "Staging") -> Dict[str, Any]:
        """
        Promote a model to a specific stage.
        
        Args:
            model_name: Name of the model
            version: Version of the model (if None, uses latest)
            stage: Target stage (Staging, Production, Archived)
            
        Returns:
            Dictionary with promotion status
        """
        try:
            if self.client is None:
                return {
                    "success": False,
                    "error": "MLflow client not initialized"
                }
            
            # Get model version
            if version is None:
                latest_version = self.client.get_latest_versions(model_name)[0]
                version = latest_version.version
            else:
                latest_version = self.client.get_model_version(model_name, version)
            
            # Transition model stage
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage
            )
            
            return {
                "success": True,
                "model_name": model_name,
                "version": version,
                "stage": stage,
                "message": f"Model '{model_name}' version {version} promoted to {stage}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to promote model: {str(e)}"
            }
    
    def list_models(self) -> Dict[str, Any]:
        """
        List all registered models.
        
        Returns:
            Dictionary with list of models
        """
        try:
            if self.client is None:
                return {
                    "success": False,
                    "error": "MLflow client not initialized"
                }
            
            models = self.client.search_registered_models()
            
            model_list = []
            for model in models:
                model_list.append({
                    "name": model.name,
                    "latest_versions": [
                        {
                            "version": version.version,
                            "stage": version.current_stage,
                            "status": version.status
                        }
                        for version in model.latest_versions
                    ]
                })
            
            return {
                "success": True,
                "models": model_list,
                "count": len(model_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list models: {str(e)}"
            }
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        try:
            if self.client is None:
                return {
                    "success": False,
                    "error": "MLflow client not initialized"
                }
            
            model = self.client.get_registered_model(model_name)
            
            return {
                "success": True,
                "model_name": model_name,
                "description": model.description,
                "latest_versions": [
                    {
                        "version": version.version,
                        "stage": version.current_stage,
                        "status": version.status,
                        "creation_timestamp": version.creation_timestamp
                    }
                    for version in model.latest_versions
                ],
                "message": f"Retrieved information for model '{model_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get model info: {str(e)}"
            }
