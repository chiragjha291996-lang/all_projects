import re
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Section:
    """Represents a document section or subsection"""
    level: int  # 1 for main section, 2 for subsection, etc.
    number: str  # e.g., "1", "1.1", "A", "I"
    title: str  # Section title
    content: str  # Section content
    start_pos: int  # Start position in original text
    end_pos: int  # End position in original text
    parent_section: Optional[str] = None  # Parent section number

class SectionChunker:
    """Advanced section-wise chunking for SOP documents"""
    
    def __init__(self):
        # Patterns for detecting different section formats
        self.section_patterns = [
            # Numbered sections: 1., 2., 3. (with space after period)
            r'^(\d+)\.\s+(.+)',
            # Subsections: 1.1, 1.2, 2.1 (with or without period)
            r'^(\d+\.\d+)\.?\s+(.+)',
            # Sub-subsections: 1.1.1, 1.1.2
            r'^(\d+\.\d+\.\d+)\.?\s+(.+)',
            # Letter sections: A., B., C.
            r'^([A-Z])\.\s+(.+)',
            # Roman numerals: I., II., III.
            r'^([IVX]+)\.\s+(.+)',
            # Alternative formats
            r'^Section\s+(\d+):?\s+(.+)',
            r'^SECTION\s+(\d+):?\s+(.+)',
            r'^(\d+)\)\s+(.+)',  # 1) format
            r'^([a-z])\)\s+(.+)',  # a) format
        ]
        
        # Common SOP section keywords
        self.sop_keywords = [
            'purpose', 'scope', 'responsibility', 'procedure', 'materials',
            'equipment', 'safety', 'precautions', 'steps', 'process',
            'instructions', 'requirements', 'specifications', 'quality',
            'control', 'documentation', 'records', 'references', 'definitions',
            'training', 'maintenance', 'troubleshooting', 'emergency',
            'procedures', 'background', 'overview', 'introduction'
        ]
        
        logger.info("Initialized SectionChunker for SOP documents")
    
    def _generate_content_hash(self, text: str) -> str:
        """
        Generate SHA-256 hash for content-based exact matching
        
        Args:
            text: Section text content
            
        Returns:
            SHA-256 hash as hexadecimal string
        """
        # Normalize text for consistent hashing
        normalized_text = text.strip().lower()
        # Remove extra whitespace
        normalized_text = re.sub(r'\s+', ' ', normalized_text)
        
        # Generate hash
        content_hash = hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()
        return content_hash
    
    def _generate_sentence_hashes(self, text: str) -> List[Dict[str, str]]:
        """
        Generate hashes for individual sentences within a section
        
        Args:
            text: Section text content
            
        Returns:
            List of sentence hash dictionaries
        """
        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+', text)
        sentence_hashes = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 10:  # Skip very short fragments
                # Normalize sentence
                normalized_sentence = sentence.lower().strip()
                normalized_sentence = re.sub(r'\s+', ' ', normalized_sentence)
                
                # Generate hash
                sentence_hash = hashlib.sha256(normalized_sentence.encode('utf-8')).hexdigest()
                
                sentence_hashes.append({
                    'sentence_index': i,
                    'sentence_text': sentence,
                    'sentence_hash': sentence_hash,
                    'word_count': len(sentence.split())
                })
        
        return sentence_hashes
    
    def detect_sections(self, text: str) -> List[Section]:
        """
        Detect sections and subsections in the document text
        
        Args:
            text: Document text content
            
        Returns:
            List of detected sections
        """
        sections = []
        lines = text.split('\n')
        current_section = None
        content_buffer = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this line is a section header
            section_match = self._match_section_header(line_stripped) if line_stripped else None
            
            if section_match:
                # Save previous section if exists
                if current_section:
                    current_section.content = '\n'.join(content_buffer).strip()
                    current_section.end_pos = self._get_text_position(text, i)
                    sections.append(current_section)
                
                # Create new section
                level, number, title = section_match
                current_section = Section(
                    level=level,
                    number=number,
                    title=title,
                    content='',
                    start_pos=self._get_text_position(text, i),
                    end_pos=0,
                    parent_section=self._find_parent_section(number, sections)
                )
                content_buffer = []
                
            else:
                # Add line to current section content (including empty lines for structure)
                if current_section:  # Only add if we have a current section
                    content_buffer.append(line_stripped)
        
        # Save the last section
        if current_section:
            current_section.content = '\n'.join(content_buffer).strip()
            current_section.end_pos = len(text)
            sections.append(current_section)
        
        # If no sections detected, create a single section
        if not sections:
            sections.append(Section(
                level=1,
                number="1",
                title="Document Content",
                content=text.strip(),
                start_pos=0,
                end_pos=len(text)
            ))
        
        logger.info(f"Detected {len(sections)} sections in document")
        return sections
    
    def _match_section_header(self, line: str) -> Optional[Tuple[int, str, str]]:
        """
        Check if a line matches any section header pattern
        
        Returns:
            Tuple of (level, number, title) if match found, None otherwise
        """
        # Check numbered patterns first (most specific)
        for pattern in self.section_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                number = match.group(1)
                title = match.group(2).strip() if len(match.groups()) > 1 else line
                level = self._determine_section_level(number)
                
                # Validate this looks like a real section
                if self._is_valid_section(title):
                    return (level, number, title)
        
        # Check for keyword-based sections (disabled for now to avoid false positives)
        # if self._contains_sop_keywords(line):
        #     return (1, "auto", line.strip())
        
        return None
    
    def _determine_section_level(self, number: str) -> int:
        """Determine the hierarchical level of a section"""
        if re.match(r'^\d+$', number):  # 1, 2, 3
            return 1
        elif re.match(r'^\d+\.\d+$', number):  # 1.1, 1.2
            return 2
        elif re.match(r'^\d+\.\d+\.\d+$', number):  # 1.1.1, 1.1.2
            return 3
        elif re.match(r'^[A-Z]$', number):  # A, B, C
            return 1
        elif re.match(r'^[IVX]+$', number):  # I, II, III
            return 1
        elif re.match(r'^[a-z]$', number):  # a, b, c
            return 2
        else:
            return 1
    
    def _is_valid_section(self, title: str) -> bool:
        """Check if a title looks like a valid section header"""
        # Must have some meaningful content
        if len(title.strip()) < 2:
            return False
        
        # Should not be too long (likely not a header)
        if len(title) > 100:
            return False
        
        # Should not be all numbers or special characters
        if re.match(r'^[\d\s\.\-_]+$', title):
            return False
        
        return True
    
    def _contains_sop_keywords(self, line: str) -> bool:
        """Check if line contains SOP-specific keywords"""
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in self.sop_keywords)
    
    def _find_parent_section(self, number: str, existing_sections: List[Section]) -> Optional[str]:
        """Find the parent section for hierarchical numbering"""
        if '.' in number and number != "auto":
            # For 1.1, parent is 1
            # For 1.1.1, parent is 1.1
            parts = number.split('.')
            if len(parts) > 1:
                parent_number = '.'.join(parts[:-1])
                # Check if parent section exists
                for section in existing_sections:
                    if section.number == parent_number:
                        return parent_number
        return None
    
    def _get_text_position(self, text: str, line_index: int) -> int:
        """Get character position in text from line index"""
        lines = text.split('\n')
        position = 0
        for i in range(min(line_index, len(lines))):
            position += len(lines[i]) + 1  # +1 for newline
        return position
    
    def create_section_chunks(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """
        Create chunks based on detected sections
        
        Args:
            text: Document text content
            filename: Name of the source document
            
        Returns:
            List of chunk dictionaries with section metadata
        """
        sections = self.detect_sections(text)
        chunks = []
        
        for i, section in enumerate(sections):
            # Skip very small sections (likely headers only)
            if len(section.content.strip()) < 50:
                continue
            
            # Generate content hash for exact matching
            content_hash = self._generate_content_hash(section.content)
            
            # Generate sentence-level hashes
            sentence_hashes = self._generate_sentence_hashes(section.content)
            
            chunk = {
                'text': section.content,
                'content_hash': content_hash,
                'sentence_hashes': sentence_hashes,
                'metadata': {
                    'chunk_index': i,
                    'section_level': section.level,
                    'section_number': section.number,
                    'section_title': section.title,
                    'parent_section': section.parent_section or 'none',
                    'start_char': section.start_pos,
                    'end_char': section.end_pos,
                    'char_count': len(section.content),
                    'word_count': len(section.content.split()) if section.content else 0,
                    'chunk_type': 'section_based',
                    'filename': filename,
                    'content_hash': content_hash,
                    'hash_type': 'content',
                    'sentence_count': len(sentence_hashes)
                }
            }
            chunks.append(chunk)
        
        # If sections are too large, further subdivide them
        refined_chunks = []
        for chunk in chunks:
            if chunk['metadata']['char_count'] > 2000:  # Large section
                sub_chunks = self._subdivide_large_section(chunk)
                refined_chunks.extend(sub_chunks)
            else:
                refined_chunks.append(chunk)
        
        logger.info(f"Created {len(refined_chunks)} section-based chunks for {filename}")
        return refined_chunks
    
    def _subdivide_large_section(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Subdivide large sections into smaller, meaningful chunks
        """
        content = chunk['text']
        metadata = chunk['metadata']
        
        # Try to split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) <= 1:
            # No clear paragraphs, split by sentences
            sentences = re.split(r'[.!?]+\s+', content)
            paragraphs = []
            current_para = ""
            for sentence in sentences:
                if len(current_para + sentence) < 1000:
                    current_para += sentence + ". "
                else:
                    if current_para:
                        paragraphs.append(current_para.strip())
                    current_para = sentence + ". "
            if current_para:
                paragraphs.append(current_para.strip())
        
        # Create sub-chunks
        sub_chunks = []
        for i, para in enumerate(paragraphs):
            if len(para.strip()) < 30:  # Skip very small paragraphs
                continue
                
            # Generate hash for subdivided content
            sub_content_hash = self._generate_content_hash(para)
            
            sub_chunk = {
                'text': para,
                'content_hash': sub_content_hash,
                'metadata': {
                    **metadata,
                    'chunk_index': f"{metadata['chunk_index']}.{i}",
                    'sub_chunk_index': i,
                    'char_count': len(para),
                    'word_count': len(para.split()),
                    'chunk_type': 'section_subdivision',
                    'content_hash': sub_content_hash,
                    'hash_type': 'content'
                }
            }
            sub_chunks.append(sub_chunk)
        
        return sub_chunks if sub_chunks else [chunk]  # Return original if subdivision failed
    
    def get_section_hierarchy(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a hierarchical representation of the document structure
        """
        hierarchy = {
            'document_structure': {},
            'section_count': 0,
            'subsection_count': 0,
            'total_chunks': len(chunks)
        }
        
        for chunk in chunks:
            metadata = chunk['metadata']
            level = metadata.get('section_level', 1)
            number = metadata.get('section_number', 'unknown')
            title = metadata.get('section_title', 'Untitled')
            
            if level == 1:
                hierarchy['section_count'] += 1
                hierarchy['document_structure'][number] = {
                    'title': title,
                    'subsections': {},
                    'chunk_count': 1
                }
            elif level == 2:
                hierarchy['subsection_count'] += 1
                parent = metadata.get('parent_section')
                if parent and parent in hierarchy['document_structure']:
                    hierarchy['document_structure'][parent]['subsections'][number] = {
                        'title': title,
                        'chunk_count': 1
                    }
                    hierarchy['document_structure'][parent]['chunk_count'] += 1
        
        return hierarchy
