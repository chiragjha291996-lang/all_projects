# SOP Insight Engine MVP

AI-powered Standard Operating Procedure analysis tool for manufacturing environments.

## Features

- **File Upload**: Upload individual PDF and DOCX SOP files
- **LLM-based Analysis**: Uses Google Gemini API for semantic similarity analysis
- **Embedding-based Processing**: Breaks documents into semantic chunks using sentence transformers
- **Smart Clustering**: Groups semantically similar SOPs using embeddings + LLM analysis
- **Difference Detection**: Identifies key differences between procedures at chunk and document level

## Project Structure

```
Manufacturing SOP standardization/
├── backend/
│   ├── app.py                  # Flask API server
│   ├── document_processor.py   # Text extraction from PDF/DOCX with chunking
│   ├── embedding_service.py    # Embedding-based document processing
│   ├── llm_service.py         # LLM integration for analysis
│   ├── requirements.txt       # Python dependencies
│   ├── env_example.txt        # Environment variables template
│   ├── ollama_setup.md        # Ollama setup guide
│   └── uploads/              # Uploaded files directory
├── frontend/
│   └── index.html            # Simple HTML interface (legacy)
├── frontend-react/           # Modern React TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API service layer
│   │   ├── types.ts          # TypeScript type definitions
│   │   └── App.tsx           # Main application
│   └── package.json          # React dependencies
├── PRD                       # Product Requirements Document
└── README.md                 # This file
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get Gemini API Key:**
   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key for Google Gemini
   - Copy the API key

5. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   # Edit .env file and add your Gemini API key:
   # GEMINI_API_KEY=your_actual_api_key_here
   ```

6. **Run the Flask server:**
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5001`

### Frontend Setup (React)

1. **Navigate to React frontend directory:**
   ```bash
   cd frontend-react
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   PORT=3001 npm start
   ```
   
   The React app will be available at `http://localhost:3001`

#### Alternative: Simple HTML Frontend

For a basic interface without React:

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Open the web interface:**
   Open `index.html` in your web browser, or serve it using a simple HTTP server:
   ```bash
   python -m http.server 8080
   ```
   
   Then access: `http://localhost:8080`

## Usage

1. **Upload SOPs**: Upload 2 SOP files (PDF or DOCX format)
2. **AI Analysis**: Click "Analyze SOPs with AI" to process documents
3. **View Results**: Review semantic clustering and similarity analysis
4. **Examine Differences**: See detailed breakdown of procedural differences

## API Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload SOP files
- `GET /files` - List uploaded files
- `POST /process` - Process documents and perform clustering
- `POST /similarity` - Analyze similarity between two specific files

## Requirements

- Python 3.8+
- Google Gemini API key
- Modern web browser

## MVP Focus

This implementation focuses on:
- Individual file upload (not folder upload)
- 2 SOP comparison and analysis
- Embedding-based semantic chunking and similarity
- Combined embeddings + LLM analysis for accuracy
- Chunk-level and document-level clustering
- Future expansion for detailed difference detection

## Next Steps

- Implement detailed difference highlighting
- Add parameter mismatch detection
- Enhance clustering for multiple documents
- Add export functionality for analysis results
