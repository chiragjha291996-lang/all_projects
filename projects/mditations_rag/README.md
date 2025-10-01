# Meditations RAG System

A Retrieval-Augmented Generation (RAG) implementation for Marcus Aurelius's "Meditations" PDF using **free open-source components** and **Google's Gemini 2.5 Flash** model.

## Features

- **PDF Processing**: Extracts and chunks text from the Meditations PDF
- **Vector Database**: Uses ChromaDB for efficient similarity search
- **Semantic Search**: Finds relevant passages based on user queries
- **Interactive UI**: Streamlit-based web interface for querying
- **Context-Aware Responses**: Generates answers using retrieved context
- **Free & Open Source**: Uses free components and Gemini 2.5 Flash model

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env_example.txt .env
# Edit .env with your Google API key
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `pdf_processor.py`: Handles PDF text extraction and chunking
- `vector_store.py`: Manages ChromaDB vector database operations
- `rag_engine.py`: Core RAG logic for retrieval and generation using Gemini 2.5 Flash
- `app.py`: Streamlit web interface
- `utils.py`: Utility functions

## Usage

1. Start the Streamlit app
2. Enter your question about Meditations
3. Get AI-generated answers based on relevant passages from the text

## Components

### PDF Processor
- Extracts text from PDF pages
- Splits text into semantic chunks
- Handles metadata extraction

### Vector Store
- Stores document chunks as embeddings
- Enables similarity search
- Manages document metadata

### RAG Engine
- Retrieves relevant passages
- Generates contextual responses using Gemini 2.5 Flash
- Combines retrieval and generation

## Environment Variables

Create a `.env` file with:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Free & Open Source Components

- **Vector Database**: ChromaDB (free)
- **Embeddings**: Sentence Transformers (free)
- **PDF Processing**: PyPDF2 (free)
- **Web Framework**: Streamlit (free)
- **AI Model**: Google Gemini 2.5 Flash (free tier available)

## Getting Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new project
3. Get your API key
4. Add it to your `.env` file 