#!/usr/bin/env python3
"""
Setup script for Meditations RAG System
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies."""
    try:
        logger.info("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def check_pdf_file():
    """Check if PDF file exists."""
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        logger.error("No PDF file found in current directory")
        return False
    
    pdf_file = pdf_files[0]
    logger.info(f"Found PDF file: {pdf_file}")
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path('.env')
    if not env_file.exists():
        logger.info("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
        logger.info("Created .env file. Please add your Google API key.")
        return False
    else:
        logger.info(".env file already exists")
        return True

def test_imports():
    """Test if all required modules can be imported."""
    try:
        import streamlit
        import google.generativeai
        import chromadb
        import sentence_transformers
        import PyPDF2
        logger.info("All required modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("Setting up Meditations RAG System with free open-source components...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check for PDF file
    if not check_pdf_file():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Create .env file
    env_ready = create_env_file()
    
    logger.info("Setup completed!")
    
    if not env_ready:
        logger.warning("Please add your Google API key to the .env file")
        logger.info("You can get an API key from: https://aistudio.google.com/")
    
    logger.info("To run the application:")
    logger.info("1. Add your Google API key to .env file")
    logger.info("2. Run: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 