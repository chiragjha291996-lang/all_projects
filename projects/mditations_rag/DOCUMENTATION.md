# Meditations RAG System Documentation

## Overview

This is a Retrieval-Augmented Generation (RAG) system designed to answer questions about Marcus Aurelius's "Meditations" using **free open-source components** and **Google's Gemini 2.5 Flash** model. The system processes the PDF text, creates vector embeddings, and uses them to retrieve relevant passages when answering questions.

## Architecture

### Components

1. **PDF Processor** (`pdf_processor.py`)
   - Extracts text from PDF files
   - Splits text into semantic chunks
   - Handles metadata extraction

2. **Vector Store** (`vector_store.py`)
   - Manages ChromaDB vector database
   - Stores document embeddings
   - Performs similarity search

3. **RAG Engine** (`rag_engine.py`)
   - Combines retrieval and generation
   - Uses Google Gemini 2.5 Flash for text generation
   - Manages context and response creation

4. **Web Interface** (`app.py`)
   - Streamlit-based UI
   - Interactive question-answering
   - Real-time response generation

5. **Utilities** (`utils.py`)
   - Text processing functions
   - Query validation
   - Helper utilities

## Installation

### Prerequisites

- Python 3.8 or higher
- Google API key (free tier available)
- PDF file of "Meditations" by Marcus Aurelius

### Setup Steps

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your Google API key
   ```

4. **Run the setup script:**
   ```bash
   python setup.py
   ```

5. **Test the system:**
   ```bash
   python test_system.py
   ```

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will:
1. Process the PDF file (first time only)
2. Create vector embeddings
3. Start the web interface

### Using the Web Interface

1. **Ask Questions**: Enter your question about Meditations in the text area
2. **Adjust Parameters**: Use the slider to control how many context passages to retrieve
3. **View Results**: See the AI-generated answer and the source passages used
4. **Example Questions**: Click on example questions to get started

### Example Questions

- "What does Marcus Aurelius say about death?"
- "How should one deal with anger according to the Meditations?"
- "What is the Stoic view on external events?"
- "How does Marcus Aurelius advise dealing with difficult people?"

## Configuration

### Environment Variables

Create a `.env` file with:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### Vector Store Settings

The vector store uses these default settings:
- **Collection Name**: "meditations"
- **Persist Directory**: "./chroma_db"
- **Embedding Model**: "all-MiniLM-L6-v2"

### RAG Settings

- **Model**: Gemini 2.0 Flash Experimental
- **Max Output Tokens**: 1000
- **Temperature**: 0.7
- **Top-p**: 0.8
- **Top-k**: 40
- **Context Passages**: 5 (configurable)

## Free & Open Source Components

### Vector Database
- **ChromaDB**: Free, open-source vector database
- **Sentence Transformers**: Free embedding models
- **Local Storage**: No cloud costs

### PDF Processing
- **PyPDF2**: Free PDF text extraction
- **LangChain**: Free text chunking utilities

### Web Framework
- **Streamlit**: Free, open-source web framework
- **Local Deployment**: No hosting costs

### AI Model
- **Google Gemini 2.5 Flash**: Free tier available
- **High Performance**: Fast and accurate responses
- **No Training Required**: Ready to use

## Technical Details

### PDF Processing

The system uses PyPDF2 to extract text from PDF files. The text is then chunked using LangChain's RecursiveCharacterTextSplitter with:
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Separators: ["\n\n", "\n", " ", ""]

### Vector Embeddings

- **Model**: Sentence Transformers "all-MiniLM-L6-v2"
- **Dimension**: 384
- **Database**: ChromaDB with persistent storage

### Retrieval Process

1. User query is converted to embedding
2. Similarity search finds relevant passages
3. Top N passages are retrieved
4. Context is formatted for the language model

### Generation Process

1. Retrieved passages are formatted as context
2. System prompt sets the AI as a Meditations expert
3. User query and context are sent to Gemini 2.5 Flash
4. Response is generated and returned

## Getting Google API Key

1. **Visit Google AI Studio**: Go to [https://aistudio.google.com/](https://aistudio.google.com/)
2. **Create Account**: Sign up for a free Google account
3. **Get API Key**: Generate your API key from the dashboard
4. **Add to .env**: Place your key in the `.env` file

## Troubleshooting

### Common Issues

1. **"No PDF file found"**
   - Ensure the PDF file is in the project directory
   - Check file permissions

2. **"Google API key not set"**
   - Add your API key to the `.env` file
   - Get an API key from https://aistudio.google.com/

3. **Import errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **Memory issues with large PDFs**
   - Reduce chunk size in `pdf_processor.py`
   - Use smaller embedding model

5. **Slow performance**
   - Reduce number of context passages
   - Use smaller embedding model
   - Check internet connection for API calls

### Debug Mode

Enable debug logging by modifying the logging level in any module:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Testing

Run the test suite:
```bash
python test_system.py
```

This will test all components and provide detailed feedback.

## Performance Optimization

### For Large PDFs

1. **Increase chunk size** in `pdf_processor.py`
2. **Use GPU** for embeddings (if available)
3. **Batch processing** for vector storage

### For Better Responses

1. **Adjust temperature** in `rag_engine.py`
2. **Modify system prompt** for specific use cases
3. **Increase context passages** for more comprehensive answers

## Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly

2. **Input Validation**
   - All user inputs are sanitized
   - Query length limits are enforced
   - Special characters are filtered

3. **Data Privacy**
   - No user data is stored permanently
   - Vector database contains only document content
   - API calls are not logged

## Extending the System

### Adding New Documents

1. Replace the PDF file
2. Clear the vector store: `vector_store.clear_collection()`
3. Restart the application

### Customizing the Model

Modify `rag_engine.py` to use different Gemini models:
```python
self.model = genai.GenerativeModel('gemini-1.5-flash')  # Change model here
```

### Adding New Features

1. **Custom Embeddings**: Modify `vector_store.py`
2. **Different Chunking**: Update `pdf_processor.py`
3. **Enhanced UI**: Extend `app.py`

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test suite
3. Review the logs for error messages
4. Ensure all dependencies are installed

## License

This project is for educational and personal use. Please respect the original text copyrights. 