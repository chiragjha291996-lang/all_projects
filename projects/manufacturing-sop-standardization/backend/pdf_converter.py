import pdfplumber
import json
import os
import hashlib
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PDFToHTMLConverter:
    def __init__(self):
        self.output_dir = "./converted_documents"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def convert_pdf_to_html(self, pdf_path: str, document_name: str) -> Dict[str, Any]:
        """Convert PDF to HTML with enhanced visual structure"""
        logger.info(f"Converting PDF to HTML: {pdf_path}")
        
        pages_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num} of {len(pdf.pages)}")
                    
                    # Extract text with position information
                    text_objects = page.chars  # Character-level positioning
                    words = page.extract_words()  # Word-level positioning
                    lines = page.extract_text_simple()  # Line-level text
                    
                    # Create enhanced HTML for this page
                    page_html = self._create_enhanced_page_html(page_num, text_objects, words, lines, page.width, page.height)
                    
                    pages_data.append({
                        'page_number': page_num,
                        'html_content': page_html,
                        'text_objects': text_objects,
                        'words': words,
                        'lines': lines,
                        'page_width': page.width,
                        'page_height': page.height,
                        'char_count': len(text_objects),
                        'word_count': len(words)
                    })
            
            # Save HTML file with enhanced styling
            html_file = os.path.join(self.output_dir, f"{document_name}.html")
            self._save_enhanced_html_file(html_file, pages_data, document_name)
            
            logger.info(f"Successfully converted PDF to HTML: {html_file}")
            
            return {
                'html_file': html_file,
                'total_pages': len(pages_data),
                'pages_data': pages_data,
                'document_name': document_name
            }
            
        except Exception as e:
            logger.error(f"Error converting PDF to HTML: {str(e)}")
            raise
    
    def _create_enhanced_page_html(self, page_num: int, text_objects: List, words: List, lines: str, page_width: float, page_height: float) -> str:
        """Create enhanced HTML structure for a single page with better visuals"""
        
        html = f'''
        <div class="pdf-page" 
             data-page="{page_num}" 
             data-page-width="{page_width}" 
             data-page-height="{page_height}">
            <div class="page-header">
                <span class="page-number">Page {page_num}</span>
                <span class="page-info">{len(words)} words, {len(text_objects)} characters</span>
            </div>
            <div class="page-content">
        '''
        
        # Group words into lines for better structure
        if words:
            current_line_y = words[0]['top'] if words else 0
            line_words = []
            
            for word in words:
                # If Y position is significantly different, start new line
                if abs(word['top'] - current_line_y) > 5:  # 5px tolerance
                    if line_words:
                        html += self._create_line_html(line_words)
                    line_words = [word]
                    current_line_y = word['top']
                else:
                    line_words.append(word)
            
            # Add the last line
            if line_words:
                html += self._create_line_html(line_words)
        
        html += '''
            </div>
        </div>
        '''
        
        return html
    
    def _create_line_html(self, words: List[Dict]) -> str:
        """Create HTML for a line of words with positioning"""
        if not words:
            return ""
        
        # Calculate line bounds
        min_x = min(word['x0'] for word in words)
        max_x = max(word['x1'] for word in words)
        y = words[0]['top']
        height = max(word['bottom'] - word['top'] for word in words)
        
        line_html = f'''
        <div class="text-line" 
             style="left: {min_x}px; top: {y}px; width: {max_x - min_x}px; height: {height}px;">
        '''
        
        for word in words:
            word_id = hashlib.md5(f"{word['text']}_{word['x0']}_{word['top']}".encode()).hexdigest()[:8]
            
            # Calculate width and height from coordinates
            word_width = word['x1'] - word['x0']
            word_height = word['bottom'] - word['top']
            
            line_html += f'''
            <span class="word" 
                  id="word-{word_id}"
                  data-word-id="{word_id}"
                  data-text="{word['text']}"
                  data-x="{word['x0']}" 
                  data-y="{word['top']}" 
                  data-width="{word_width}" 
                  data-height="{word_height}"
                  data-font-size="12"
                  data-font-family="Arial"
                  style="left: {word['x0'] - min_x}px; top: {word['top'] - y}px; width: {word_width}px; height: {word_height}px;">
                {word['text']}
            </span>
            '''
        
        line_html += '</div>'
        return line_html
    
    def _save_enhanced_html_file(self, html_file: str, pages_data: List[Dict], document_name: str):
        """Save complete HTML file with enhanced CSS and JavaScript"""
        
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{document_name} - PDF Viewer</title>
            <style>
                {self._get_enhanced_css_styles()}
            </style>
        </head>
        <body>
            <div class="document-container">
                <div class="document-header">
                    <h1>{document_name}</h1>
                    <div class="document-stats">
                        <span>Total Pages: {len(pages_data)}</span>
                        <span>Total Words: {sum(page['word_count'] for page in pages_data)}</span>
                    </div>
                </div>
                
                <div class="pages-container">
                    {self._render_all_pages(pages_data)}
                </div>
            </div>
            
            <script>
                {self._get_enhancement_javascript()}
            </script>
        </body>
        </html>
        '''
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _get_enhanced_css_styles(self) -> str:
        """Enhanced CSS styles for better PDF rendering and highlighting"""
        return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .document-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .document-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            text-align: center;
        }
        
        .document-header h1 {
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .document-stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 14px;
            opacity: 0.9;
        }
        
        .pages-container {
            padding: 30px;
        }
        
        .pdf-page {
            position: relative;
            width: 100%;
            max-width: 800px;
            margin: 0 auto 40px auto;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            background: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .pdf-page:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .page-header {
            background: #f8f9fa;
            padding: 12px 20px;
            border-bottom: 1px solid #e1e5e9;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #6c757d;
        }
        
        .page-number {
            font-weight: 600;
            color: #495057;
        }
        
        .page-content {
            position: relative;
            min-height: 600px;
            padding: 20px;
            background: white;
        }
        
        .text-line {
            position: absolute;
            display: flex;
            align-items: center;
        }
        
        .word {
            position: absolute;
            font-family: inherit;
            line-height: 1.2;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 2px;
            padding: 1px 2px;
        }
        
        .word:hover {
            background-color: rgba(0, 123, 255, 0.1);
            transform: scale(1.05);
        }
        
        /* Highlighting Styles */
        .highlight-exact-match {
            background-color: rgba(40, 167, 69, 0.4) !important;
            border: 2px solid #28a745 !important;
            box-shadow: 0 0 8px rgba(40, 167, 69, 0.3) !important;
            animation: pulse-green 2s infinite;
        }
        
        .highlight-semantic-similar {
            background-color: rgba(255, 193, 7, 0.4) !important;
            border: 2px solid #ffc107 !important;
            box-shadow: 0 0 8px rgba(255, 193, 7, 0.3) !important;
            animation: pulse-yellow 2s infinite;
        }
        
        .highlight-unique-doc1 {
            background-color: rgba(220, 53, 69, 0.4) !important;
            border: 2px solid #dc3545 !important;
            box-shadow: 0 0 8px rgba(220, 53, 69, 0.3) !important;
            animation: pulse-red 2s infinite;
        }
        
        .highlight-unique-doc2 {
            background-color: rgba(23, 162, 184, 0.4) !important;
            border: 2px solid #17a2b8 !important;
            box-shadow: 0 0 8px rgba(23, 162, 184, 0.3) !important;
            animation: pulse-blue 2s infinite;
        }
        
        .highlight-different {
            background-color: rgba(108, 117, 125, 0.4) !important;
            border: 2px solid #6c757d !important;
            box-shadow: 0 0 8px rgba(108, 117, 125, 0.3) !important;
            animation: pulse-gray 2s infinite;
        }
        
        /* Animations */
        @keyframes pulse-green {
            0%, 100% { box-shadow: 0 0 8px rgba(40, 167, 69, 0.3); }
            50% { box-shadow: 0 0 15px rgba(40, 167, 69, 0.6); }
        }
        
        @keyframes pulse-yellow {
            0%, 100% { box-shadow: 0 0 8px rgba(255, 193, 7, 0.3); }
            50% { box-shadow: 0 0 15px rgba(255, 193, 7, 0.6); }
        }
        
        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 8px rgba(220, 53, 69, 0.3); }
            50% { box-shadow: 0 0 15px rgba(220, 53, 69, 0.6); }
        }
        
        @keyframes pulse-blue {
            0%, 100% { box-shadow: 0 0 8px rgba(23, 162, 184, 0.3); }
            50% { box-shadow: 0 0 15px rgba(23, 162, 184, 0.6); }
        }
        
        @keyframes pulse-gray {
            0%, 100% { box-shadow: 0 0 8px rgba(108, 117, 125, 0.3); }
            50% { box-shadow: 0 0 15px rgba(108, 117, 125, 0.6); }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .document-container {
                margin: 10px;
                border-radius: 8px;
            }
            
            .document-header {
                padding: 15px 20px;
            }
            
            .document-header h1 {
                font-size: 24px;
            }
            
            .pages-container {
                padding: 20px;
            }
            
            .pdf-page {
                margin-bottom: 20px;
            }
        }
        
        /* Print Styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .document-container {
                box-shadow: none;
                border-radius: 0;
            }
            
            .document-header {
                background: white;
                color: black;
                border-bottom: 2px solid #000;
            }
            
            .pdf-page {
                box-shadow: none;
                border: 1px solid #ccc;
                page-break-after: always;
            }
        }
        '''
    
    def _get_enhancement_javascript(self) -> str:
        """JavaScript for enhanced interactivity"""
        return '''
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers for words
            document.querySelectorAll('.word').forEach(word => {
                word.addEventListener('click', function() {
                    // Remove previous selections
                    document.querySelectorAll('.word-selected').forEach(el => {
                        el.classList.remove('word-selected');
                    });
                    
                    // Add selection to clicked word
                    this.classList.add('word-selected');
                    
                    // Show word info
                    const wordId = this.dataset.wordId;
                    const text = this.dataset.text;
                    console.log(`Selected word: ${text} (ID: ${wordId})`);
                });
            });
            
            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey || e.metaKey) {
                    switch(e.key) {
                        case 'f':
                            e.preventDefault();
                            // Focus search functionality
                            console.log('Search shortcut triggered');
                            break;
                        case 'a':
                            e.preventDefault();
                            // Select all words
                            document.querySelectorAll('.word').forEach(word => {
                                word.classList.add('word-selected');
                            });
                            break;
                    }
                }
            });
            
            // Add smooth scrolling for page navigation
            const pages = document.querySelectorAll('.pdf-page');
            let currentPageIndex = 0;
            
            function scrollToPage(index) {
                if (index >= 0 && index < pages.length) {
                    pages[index].scrollIntoView({ 
                        behavior: 'smooth',
                        block: 'start'
                    });
                    currentPageIndex = index;
                }
            }
            
            // Expose functions globally for external control
            window.PDFViewer = {
                scrollToPage: scrollToPage,
                getCurrentPage: () => currentPageIndex,
                getTotalPages: () => pages.length
            };
        });
        
        // CSS for word selection
        const style = document.createElement('style');
        style.textContent = `
            .word-selected {
                background-color: rgba(0, 123, 255, 0.3) !important;
                border: 2px solid #007bff !important;
                transform: scale(1.1) !important;
                z-index: 10 !important;
            }
        `;
        document.head.appendChild(style);
        '''
    
    def _render_all_pages(self, pages_data: List[Dict]) -> str:
        """Render all pages with enhanced structure"""
        return ''.join([page['html_content'] for page in pages_data])
