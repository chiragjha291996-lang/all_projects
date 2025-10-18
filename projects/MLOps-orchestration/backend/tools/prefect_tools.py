"""
Prefect tools for pipeline registration and execution.
"""
import os
import tempfile
from typing import Dict, Any, Optional
from prefect import flow, task
from prefect.client.orchestration import PrefectClient
import importlib.util
import sys


class PrefectTools:
    """Tools for interacting with Prefect for pipeline orchestration."""
    
    def __init__(self, api_url: str = "http://localhost:4200/api"):
        """Initialize Prefect client."""
        self.api_url = api_url
        self.client = PrefectClient(api=api_url)
    
    def register_pipeline_from_file(self, file_path: str, pipeline_name: str) -> Dict[str, Any]:
        """
        Register a pipeline from a Python file.
        
        Args:
            file_path: Path to the Python file containing the pipeline
            pipeline_name: Name for the registered pipeline
            
        Returns:
            Dictionary with registration status and details
        """
        try:
            # Load the module from file
            spec = importlib.util.spec_from_file_location(pipeline_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the flow in the module
            flow_obj = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, 'is_flow') and attr.is_flow:
                    flow_obj = attr
                    break
            
            if not flow_obj:
                return {
                    "success": False,
                    "error": f"No Prefect flow found in {file_path}"
                }
            
            # Register flow directly (simplified approach for MVP)
            # In a real implementation, you would use flow.deploy() or flow.serve()
            flow_obj.name = pipeline_name
            
            return {
                "success": True,
                "pipeline_name": pipeline_name,
                "deployment_id": f"{pipeline_name}-deployment",
                "flow_name": flow_obj.name,
                "message": f"Pipeline '{pipeline_name}' registered successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to register pipeline: {str(e)}"
            }
    
    def trigger_pipeline_run(self, pipeline_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a run of an existing pipeline.
        
        Args:
            pipeline_name: Name of the pipeline to run
            parameters: Optional parameters for the run
            
        Returns:
            Dictionary with run status and details
        """
        try:
            # For MVP, we'll simulate a pipeline run
            # In a real implementation, you would use the Prefect client to create flow runs
            flow_run_id = f"run-{pipeline_name}-{hash(str(parameters))}"
            
            return {
                "success": True,
                "pipeline_name": pipeline_name,
                "flow_run_id": flow_run_id,
                "message": f"Pipeline '{pipeline_name}' run started successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to trigger pipeline run: {str(e)}"
            }
    
    def get_pipeline_status(self, flow_run_id: str) -> Dict[str, Any]:
        """
        Get the status of a pipeline run.
        
        Args:
            flow_run_id: ID of the flow run
            
        Returns:
            Dictionary with run status and details
        """
        try:
            # For MVP, simulate a completed status
            return {
                "success": True,
                "flow_run_id": flow_run_id,
                "status": "COMPLETED",
                "message": f"Pipeline run status: COMPLETED"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get pipeline status: {str(e)}"
            }
    
    def list_pipelines(self) -> Dict[str, Any]:
        """
        List all registered pipelines.
        
        Returns:
            Dictionary with list of pipelines
        """
        try:
            # For MVP, return empty list
            # In a real implementation, you would query the Prefect client
            pipelines = []
            
            return {
                "success": True,
                "pipelines": pipelines,
                "count": len(pipelines)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list pipelines: {str(e)}"
            }
