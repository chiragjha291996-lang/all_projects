import PyPDF2
import os
from typing import List, Dict, Any
import logging
import re
from utils import remove_end_of_page_footnotes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and paragraph-based chunking for RAG system."""
    
    def __init__(self, pdf_path: str = None):
        if pdf_path is None:
            pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
            if pdf_files:
                self.pdf_path = pdf_files[0]
            else:
                raise FileNotFoundError("No PDF file found in current directory")
        else:
            self.pdf_path = pdf_path
    
    def extract_text_from_pdf(self) -> str:
        """Extract all text from the PDF file."""
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            logger.info(f"Processing PDF: {self.pdf_path}")
            logger.info(f"Total pages: {len(pdf_reader.pages)}")
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n\n--- Page {page_num + 1} ---\n\n"
                text += page_text if page_text else ""
                if page_num % 10 == 0:
                    logger.info(f"Processed page {page_num + 1}")
            logger.info("PDF text extraction completed")
            return text
    
    def paragraph_chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks at paragraph markers like 3.1, 3.2, etc."""
        # Regex: match paragraph markers at the start of a line (optionally after whitespace)
        pattern = re.compile(r'(\n|^)(\d+\.\d+)', re.MULTILINE)
        splits = [m.start(2) for m in pattern.finditer(text)]
        splits.append(len(text))
        chunks = []
        for i in range(len(splits) - 1):
            start = splits[i]
            end = splits[i+1]
            chunk = text[start:end].strip()
            if chunk and len(chunk) > 20:
                marker_match = re.match(r'^(\d+\.\d+)', chunk)
                marker = marker_match.group(1) if marker_match else f"chunk_{i}"
                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "chunk_id": i,
                        "marker": marker,
                        "source": "meditations_pdf",
                        "chunk_size": len(chunk)
                    }
                })
        logger.info(f"Paragraph chunking produced {len(chunks)} chunks.")
        return chunks
    
    def process_pdf(self) -> List[Dict[str, Any]]:
        """Complete PDF processing pipeline using paragraph chunking, with footnote removal."""
        logger.info("Starting PDF processing pipeline with paragraph chunking")
        text = self.extract_text_from_pdf()
        text = remove_end_of_page_footnotes(text)
        chunks = self.paragraph_chunk_text(text)
        logger.info(f"PDF processing completed. Created {len(chunks)} paragraph chunks.")
        return chunks

if __name__ == "__main__":
    processor = PDFProcessor()
    chunks = processor.process_pdf()
    print(f"Processed {len(chunks)} paragraph chunks.")
    print(f"First chunk preview: {chunks[0]['content'][:200]}...") 