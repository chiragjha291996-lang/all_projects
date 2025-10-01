import re
import os
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text content.
    
    Args:
        text: Raw text to clean.
        
    Returns:
        Cleaned text.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text.strip()

def validate_pdf_path(pdf_path: str) -> bool:
    """Validate that a PDF file exists and is accessible.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        True if valid, False otherwise.
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return False
    
    if not pdf_path.lower().endswith('.pdf'):
        logger.error(f"File is not a PDF: {pdf_path}")
        return False
    
    if os.path.getsize(pdf_path) == 0:
        logger.error(f"PDF file is empty: {pdf_path}")
        return False
    
    return True

def chunk_text_by_sentences(text: str, max_chunk_size: int = 1000) -> List[str]:
    """Split text into chunks based on sentence boundaries.
    
    Args:
        text: Text to chunk.
        max_chunk_size: Maximum size of each chunk.
        
    Returns:
        List of text chunks.
    """
    # Split by sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
    """Extract metadata from PDF filename.
    
    Args:
        filename: Name of the PDF file.
        
    Returns:
        Dictionary of metadata.
    """
    metadata = {
        "filename": filename,
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "source": "pdf"
    }
    
    # Try to extract more information from filename
    if "annotated" in filename.lower():
        metadata["edition"] = "annotated"
    
    if "waterfield" in filename.lower():
        metadata["editor"] = "Robin Waterfield"
    
    return metadata

def format_context_for_display(context: List[Dict[str, Any]]) -> str:
    """Format context for display in the UI.
    
    Args:
        context: List of context documents.
        
    Returns:
        Formatted string for display.
    """
    formatted = []
    
    for i, doc in enumerate(context, 1):
        content = doc.get('content', '')
        distance = doc.get('distance', 0)
        
        # Truncate content if too long
        if len(content) > 500:
            content = content[:500] + "..."
        
        formatted.append(f"Passage {i} (Relevance: {1-distance:.3f}):\n{content}\n")
    
    return "\n".join(formatted)

def validate_query(query: str) -> bool:
    """Validate user query.
    
    Args:
        query: User's question.
        
    Returns:
        True if valid, False otherwise.
    """
    if not query or not query.strip():
        return False
    
    if len(query.strip()) < 3:
        return False
    
    if len(query) > 1000:
        return False
    
    return True

def sanitize_query(query: str) -> str:
    """Sanitize user query for safe processing.
    
    Args:
        query: Raw user query.
        
    Returns:
        Sanitized query.
    """
    # Remove potentially harmful characters
    query = re.sub(r'[<>"\']', '', query)
    
    # Normalize whitespace
    query = re.sub(r'\s+', ' ', query)
    
    return query.strip()

def calculate_similarity_score(distance: float) -> float:
    """Convert distance to similarity score.
    
    Args:
        distance: Distance from vector search.
        
    Returns:
        Similarity score between 0 and 1.
    """
    # Convert distance to similarity (lower distance = higher similarity)
    return max(0, 1 - distance)

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        File size in MB.
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def remove_end_of_page_footnotes(text: str) -> str:
    """Remove end-of-page footnotes from extracted PDF text.
    Footnotes are lines at the end of a page that start with a number and a period or bracket (e.g., '1. text' or '[1] text').
    """
    # Use the same page marker as in extract_text_from_pdf
    page_marker_pattern = r'\n\n--- Page (\d+) ---\n\n'
    pages = re.split(page_marker_pattern, text)
    cleaned_pages = []
    # pages will be like: [before first page, '1', page1, '2', page2, ...]
    # We want to keep the page numbers and clean the page text
    i = 0
    while i < len(pages):
        if i == 0:
            # Text before first page marker
            cleaned_pages.append(pages[i])
            i += 1
        else:
            # Page number and page text
            page_num = pages[i]
            page_text = pages[i+1]
            lines = page_text.strip().split('\n')
            # Remove trailing lines that match footnote pattern
            while lines and re.match(r'^(\d+\.|\[\d+\])', lines[-1].strip()):
                lines.pop()
            cleaned_page = '\n'.join(lines)
            cleaned_pages.append(f'--- Page {page_num} ---\n\n{cleaned_page}')
            i += 2
    return '\n\n'.join(cleaned_pages)

if __name__ == "__main__":
    # Test utility functions
    test_text = "This is a test text. It has multiple sentences. Let's see how it works."
    chunks = chunk_text_by_sentences(test_text, 50)
    print(f"Chunks: {chunks}")
    
    test_query = "What does Marcus Aurelius say about death?"
    print(f"Query valid: {validate_query(test_query)}")
    print(f"Sanitized query: {sanitize_query(test_query)}") 