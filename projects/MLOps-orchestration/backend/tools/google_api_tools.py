"""
Google APIs integration for enhanced capabilities.
"""
import os
from typing import Dict, Any, Optional
from google.cloud import storage
from google.cloud import aiplatform
from google.auth import default
import json


class GoogleAPITools:
    """Tools for integrating with Google Cloud APIs."""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize Google Cloud clients."""
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        
        if self.project_id:
            # Initialize AI Platform
            aiplatform.init(project=self.project_id)
            
            # Initialize Storage client
            self.storage_client = storage.Client(project=self.project_id)
        else:
            self.storage_client = None
    
    def upload_to_gcs(self, bucket_name: str, file_path: str, destination_name: str) -> Dict[str, Any]:
        """
        Upload a file to Google Cloud Storage.
        
        Args:
            bucket_name: Name of the GCS bucket
            file_path: Local path to the file
            destination_name: Name for the file in GCS
            
        Returns:
            Dictionary with upload status
        """
        try:
            if not self.storage_client:
                return {
                    "success": False,
                    "error": "Google Cloud Storage client not initialized"
                }
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(destination_name)
            
            blob.upload_from_filename(file_path)
            
            return {
                "success": True,
                "bucket_name": bucket_name,
                "destination_name": destination_name,
                "gs_uri": f"gs://{bucket_name}/{destination_name}",
                "message": f"File uploaded to gs://{bucket_name}/{destination_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to upload to GCS: {str(e)}"
            }
    
    def download_from_gcs(self, bucket_name: str, source_name: str, destination_path: str) -> Dict[str, Any]:
        """
        Download a file from Google Cloud Storage.
        
        Args:
            bucket_name: Name of the GCS bucket
            source_name: Name of the file in GCS
            destination_path: Local path to save the file
            
        Returns:
            Dictionary with download status
        """
        try:
            if not self.storage_client:
                return {
                    "success": False,
                    "error": "Google Cloud Storage client not initialized"
                }
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(source_name)
            
            blob.download_to_filename(destination_path)
            
            return {
                "success": True,
                "bucket_name": bucket_name,
                "source_name": source_name,
                "destination_path": destination_path,
                "message": f"File downloaded from gs://{bucket_name}/{source_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to download from GCS: {str(e)}"
            }
    
    def list_gcs_buckets(self) -> Dict[str, Any]:
        """
        List all GCS buckets in the project.
        
        Returns:
            Dictionary with list of buckets
        """
        try:
            if not self.storage_client:
                return {
                    "success": False,
                    "error": "Google Cloud Storage client not initialized"
                }
            
            buckets = list(self.storage_client.list_buckets())
            
            bucket_list = []
            for bucket in buckets:
                bucket_list.append({
                    "name": bucket.name,
                    "location": bucket.location,
                    "created": bucket.time_created
                })
            
            return {
                "success": True,
                "buckets": bucket_list,
                "count": len(bucket_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list GCS buckets: {str(e)}"
            }
    
    def deploy_model_to_ai_platform(self, model_name: str, model_uri: str, endpoint_name: str) -> Dict[str, Any]:
        """
        Deploy a model to AI Platform.
        
        Args:
            model_name: Name of the model
            model_uri: URI of the model (GCS path)
            endpoint_name: Name for the endpoint
            
        Returns:
            Dictionary with deployment status
        """
        try:
            if not self.project_id:
                return {
                    "success": False,
                    "error": "Google Cloud project not configured"
                }
            
            # Create endpoint
            endpoint = aiplatform.Endpoint.create(
                display_name=endpoint_name,
                project=self.project_id
            )
            
            # Deploy model
            model = aiplatform.Model.upload(
                display_name=model_name,
                artifact_uri=model_uri,
                serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-0:latest"
            )
            
            endpoint.deploy(
                model=model,
                deployed_model_display_name=f"{model_name}-deployment",
                machine_type="n1-standard-4"
            )
            
            return {
                "success": True,
                "model_name": model_name,
                "endpoint_name": endpoint_name,
                "endpoint_id": endpoint.resource_name,
                "message": f"Model '{model_name}' deployed to endpoint '{endpoint_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to deploy model to AI Platform: {str(e)}"
            }
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        Get information about the Google Cloud project.
        
        Returns:
            Dictionary with project information
        """
        try:
            if not self.project_id:
                return {
                    "success": False,
                    "error": "Google Cloud project not configured"
                }
            
            # Get default credentials
            credentials, project = default()
            
            return {
                "success": True,
                "project_id": self.project_id,
                "credentials_type": type(credentials).__name__,
                "message": f"Google Cloud project '{self.project_id}' is configured"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get project info: {str(e)}"
            }


