import streamlit as st
import os
import logging
from typing import Dict, Any
import time
import hashlib

from pdf_processor import PDFProcessor
from vector_store import VectorStore
from rag_engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Meditations RAG System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .answer-box {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #d3d3d3;
        margin: 1rem 0;
        font-size: 1.1rem;
        color: #222;
        min-height: 100px;
        width: 100%;
        box-sizing: border-box;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .context-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .metric-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

MODEL_OPTIONS = [
    ("Kimi K2 (moonshotai/kimi-k2:free)", "moonshotai/kimi-k2:free"),
    ("DeepSeek Chimera (tngtech/deepseek-r1t2-chimera:free)", "tngtech/deepseek-r1t2-chimera:free"),
    ("DeepSeek R1 0528 (deepseek/deepseek-r1-0528:free)", "deepseek/deepseek-r1-0528:free"),
    ("DeepSeek Chat V3 (deepseek/deepseek-chat-v3-0324:free)", "deepseek/deepseek-chat-v3-0324:free"),
    ("Qwen QWQ-32B (qwen/qwq-32b:free)", "qwen/qwq-32b:free"),
    ("DeepSeek R1 (deepseek/deepseek-r1:free)", "deepseek/deepseek-r1:free"),
]

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system components."""
    try:
        # Check if vector store has documents
        vector_store = VectorStore()
        info = vector_store.get_collection_info()
        
        if info["document_count"] == 0:
            st.info("First time setup: Processing PDF and creating vector database...")
            
            # Process PDF
            processor = PDFProcessor()
            documents = processor.process_pdf()
            
            # Add to vector store
            vector_store.add_documents(documents)
            
            st.success("PDF processed and vector database created!")
        
        # Initialize RAG engine
        rag_engine = RAGEngine(vector_store)
        return rag_engine
        
    except Exception as e:
        st.error(f"Error initializing RAG system: {e}")
        return None

def display_system_info(rag_engine: RAGEngine):
    """Display system information in the sidebar."""
    st.sidebar.markdown("## System Information")
    
    try:
        info = rag_engine.get_system_info()
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.metric("Documents", info["vector_store"]["document_count"])
        
        with col2:
            st.metric("Model", info["model"])
        
        st.sidebar.markdown(f"**Collection:** {info['vector_store']['name']}")
        st.sidebar.markdown(f"**Status:** {info['status']}")
        
    except Exception as e:
        st.sidebar.error(f"Error getting system info: {e}")

def display_context(context: list):
    """Display retrieved context passages."""
    st.markdown("### Retrieved Context")
    
    for i, doc in enumerate(context):
        with st.expander(f"Passage {i+1} (Distance: {doc['distance']:.3f})"):
            st.markdown(doc['content'])
            st.caption(f"Chunk ID: {doc['metadata']['chunk_id']}")

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">📚 Meditations RAG System</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Ask questions about Marcus Aurelius\'s "Meditations"</p>', unsafe_allow_html=True)
    
    # Sidebar: Model selection
    st.sidebar.markdown("## Select LLM Model")
    model_labels = [label for label, _ in MODEL_OPTIONS]
    model_values = [value for _, value in MODEL_OPTIONS]
    selected_model_label = st.sidebar.radio("Choose a model to use for answering:", model_labels, index=0)
    selected_model = dict(MODEL_OPTIONS)[selected_model_label]
    st.sidebar.info(f"Current model: {selected_model_label}")

    # Initialize RAG system
    rag_engine = initialize_rag_system()
    
    if rag_engine is None:
        st.error("Failed to initialize RAG system. Please check your setup.")
        return
    
    # Display system info in sidebar
    display_system_info(rag_engine)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">Ask a Question</h2>', unsafe_allow_html=True)
        
        # Query input
        query = st.text_area(
            "Enter your question about Meditations:",
            placeholder="e.g., What does Marcus Aurelius say about dealing with difficult people?",
            height=100
        )
        
        # Search parameters
        col_a, col_b = st.columns(2)
        with col_a:
            n_context = st.slider("Number of context passages", 2, 3, 2)
        with col_b:
            if st.button("Ask Question", type="primary"):
                if query.strip():
                    process_query(query, n_context, rag_engine, selected_model)
                else:
                    st.warning("Please enter a question.")
    
    with col2:
        st.markdown('<h3 class="sub-header">Example Questions</h3>', unsafe_allow_html=True)
        
        example_questions = [
            "What does Marcus Aurelius say about death?",
            "How should one deal with anger according to the Meditations?",
            "What is the Stoic view on external events?",
            "How does Marcus Aurelius advise dealing with difficult people?",
            "What does he say about living in the present moment?",
            "How should one approach their duties and responsibilities?",
            "What is the importance of reason in Stoic philosophy?",
            "How does Marcus Aurelius view the nature of the universe?"
        ]
        
        for question in example_questions:
            # Use a hash of the question for a unique key
            key = f"example_{hashlib.md5(question.encode()).hexdigest()}"
            if st.button(question, key=key):
                st.session_state.query = question
                st.rerun()

def process_query(query: str, n_context: int, rag_engine: RAGEngine, model: str):
    """Process a user query and display results."""
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Update progress
        progress_bar.progress(25)
        status_text.text("Retrieving relevant passages...")
        
        # Get answer
        start_time = time.time()
        result = rag_engine.answer_question(query, n_context, model=model)
        end_time = time.time()
        
        # Update progress
        progress_bar.progress(100)
        status_text.text("Complete!")
        
        # Display results
        st.markdown('<h2 class="sub-header">Answer</h2>', unsafe_allow_html=True)
        
        # Always show the answer in a visible, styled box
        st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Response Time", f"{end_time - start_time:.2f}s")
        
        with col2:
            st.metric("Context Passages", result["num_context_passages"])
        
        with col3:
            st.metric("Query Length", len(query))
        
        # Display context
        display_context(result["context"])
        
        # Clear progress
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"Error processing query with the LLM: {e}")
        progress_bar.empty()
        status_text.empty()

if __name__ == "__main__":
    main() 