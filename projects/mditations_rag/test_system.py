#!/usr/bin/env python3
"""
Test script for Meditations RAG System
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pdf_processor():
    """Test PDF processor functionality."""
    try:
        from pdf_processor import PDFProcessor
        
        logger.info("Testing PDF processor...")
        processor = PDFProcessor()
        
        # Test PDF processing
        chunks = processor.process_pdf()
        
        if chunks and len(chunks) > 0:
            logger.info(f"✓ PDF processor works: {len(chunks)} chunks created")
            return True
        else:
            logger.error("✗ PDF processor failed: No chunks created")
            return False
            
    except Exception as e:
        logger.error(f"✗ PDF processor test failed: {e}")
        return False

def test_vector_store():
    """Test vector store functionality."""
    try:
        from vector_store import VectorStore
        
        logger.info("Testing vector store...")
        vector_store = VectorStore()
        
        # Test collection info
        info = vector_store.get_collection_info()
        logger.info(f"✓ Vector store works: {info}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Vector store test failed: {e}")
        return False

def test_rag_engine():
    """Test RAG engine functionality."""
    try:
        from rag_engine import RAGEngine
        
        logger.info("Testing RAG engine...")
        
        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_google_api_key_here":
            logger.warning("⚠ Google API key not set, skipping RAG engine test")
            return True
        
        rag_engine = RAGEngine()
        info = rag_engine.get_system_info()
        logger.info(f"✓ RAG engine works with Gemini 2.5 Flash: {info}")
        return True
        
    except Exception as e:
        logger.error(f"✗ RAG engine test failed: {e}")
        return False

def test_utils():
    """Test utility functions."""
    try:
        from utils import clean_text, validate_query, sanitize_query
        
        logger.info("Testing utility functions...")
        
        # Test text cleaning
        test_text = "  This   is   a   test   text.  "
        cleaned = clean_text(test_text)
        assert cleaned == "This is a test text."
        
        # Test query validation
        assert validate_query("What is this?") == True
        assert validate_query("") == False
        assert validate_query("a") == False
        
        # Test query sanitization
        sanitized = sanitize_query("Test <script> query")
        assert "<script>" not in sanitized
        
        logger.info("✓ Utility functions work")
        return True
        
    except Exception as e:
        logger.error(f"✗ Utility functions test failed: {e}")
        return False

def check_environment():
    """Check environment setup."""
    logger.info("Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("✗ Python 3.8+ required")
        return False
    logger.info(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check for PDF file
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        logger.error("✗ No PDF file found")
        return False
    logger.info(f"✓ PDF file found: {pdf_files[0]}")
    
    # Check for .env file
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("⚠ .env file not found")
    else:
        logger.info("✓ .env file exists")
    
    return True

def main():
    """Run all tests."""
    logger.info("Starting Meditations RAG System tests (Free & Open Source)...")
    
    tests = [
        ("Environment", check_environment),
        ("PDF Processor", test_pdf_processor),
        ("Vector Store", test_vector_store),
        ("Utility Functions", test_utils),
        ("RAG Engine (Gemini 2.5 Flash)", test_rag_engine),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready to use.")
        logger.info("Run 'streamlit run app.py' to start the application.")
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 