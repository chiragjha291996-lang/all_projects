"""
FastAPI backend for the Conversational MLOps Agent.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import tempfile
import os
import aiofiles

from backend.agent.mlops_agent import ConversationalMLOpsAgent
from backend.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Conversational MLOps Agent",
    description="A conversational agent for MLOps workflows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = ConversationalMLOpsAgent()


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    file_path: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    success: bool
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Conversational MLOps Agent API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Agent is running"}


@app.get("/commands")
async def get_available_commands():
    """Get available commands."""
    commands = agent.get_available_commands()
    return {"commands": commands}


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message.
    
    Args:
        message: Chat message with optional file path
        
    Returns:
        Agent's response
    """
    try:
        response = agent.process_message(message.message, message.file_path)
        return ChatResponse(response=response, success=True)
    except Exception as e:
        return ChatResponse(
            response="",
            success=False,
            error=f"Failed to process message: {str(e)}"
        )


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a pipeline file.
    
    Args:
        file: Uploaded file
        
    Returns:
        Upload status and file path
    """
    # Validate file type
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python files are allowed")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        return {
            "success": True,
            "message": f"File '{file.filename}' uploaded successfully",
            "file_path": temp_file_path,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@app.post("/chat-with-file")
async def chat_with_file(
    message: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Process a chat message with an uploaded file.
    
    Args:
        message: Chat message
        file: Uploaded file
        
    Returns:
        Agent's response
    """
    try:
        # Upload file first
        upload_result = await upload_file(file)
        if not upload_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to upload file")
        
        file_path = upload_result["file_path"]
        
        # Process message with file
        response = agent.process_message(message, file_path)
        
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except:
            pass
        
        return ChatResponse(response=response, success=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@app.get("/pipelines")
async def list_pipelines():
    """List all registered pipelines."""
    try:
        result = agent.prefect_tools.list_pipelines()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list pipelines: {str(e)}")


@app.get("/models")
async def list_models():
    """List all registered models."""
    try:
        result = agent.mlflow_tools.list_models()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@app.get("/experiments")
async def list_experiments():
    """List all experiments."""
    try:
        result = agent.mlflow_tools.list_experiments()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list experiments: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
