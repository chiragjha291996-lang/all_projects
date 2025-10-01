# Manufacturing SOP Standardization

A comprehensive system for analyzing and standardizing manufacturing Standard Operating Procedures (SOPs) using AI-powered document similarity analysis.

## Project Structure

- **backend/**: Python Flask API with document processing and vector database
- **frontend-react/**: React application for file upload and analysis
- **frontend/**: Simple HTML frontend (alternative)
- **PRD**: Product Requirements Document

## Features

- Document upload and processing
- AI-powered similarity analysis
- Vector database integration
- Interactive comparison tools
- Comprehensive metrics and reporting

## Quick Start

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend-react
   npm install
   npm start
   ```

## Technologies Used

- **Backend**: Python, Flask, ChromaDB, OpenAI Embeddings
- **Frontend**: React, TypeScript, HTML/CSS
- **Database**: ChromaDB (Vector Database)
- **AI**: OpenAI GPT for embeddings and analysis

## API Endpoints

- `POST /upload` - Upload documents for analysis
- `POST /analyze` - Analyze document similarity
- `GET /health` - Health check endpoint

## Contributing

This project is part of a larger multi-project repository. See the main README for overall project guidelines.
