import logging
import json
import os
from typing import List, Dict, Any, Set, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class ExactMatchService:
    """Service for exact content matching using content hashes and sentence-level matching"""
    
    def __init__(self):
        # Hash to document mapping for fast lookups
        self.hash_to_documents: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # Document to hashes mapping
        self.document_to_hashes: Dict[str, Set[str]] = defaultdict(set)
        # Sentence hash to document mapping
        self.sentence_hash_to_documents: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # Document to sentence hashes mapping
        self.document_to_sentence_hashes: Dict[str, Set[str]] = defaultdict(set)
        
        # Persistence file
        self.persistence_file = "./exact_match_data.json"
        
        # Load existing data
        self._load_data()
        
        logger.info("Initialized ExactMatchService for content and sentence-based matching")
    
    def add_document_chunks(self, document_name: str, chunks: List[Dict[str, Any]]) -> None:
        """
        Add document chunks to the exact matching index
        
        Args:
            document_name: Name of the document
            chunks: List of chunks with content_hash
        """
        try:
            for chunk in chunks:
                content_hash = chunk.get('content_hash')
                if not content_hash:
                    continue
                
                # Create chunk reference
                chunk_ref = {
                    'document_name': document_name,
                    'chunk_index': chunk.get('metadata', {}).get('chunk_index', 0),
                    'section_number': chunk.get('metadata', {}).get('section_number', 'unknown'),
                    'section_title': chunk.get('metadata', {}).get('section_title', 'unknown'),
                    'content': chunk['text'],  # Store full content, not just preview
                    'text_preview': chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text'],
                    'word_count': chunk.get('metadata', {}).get('word_count', 0),
                    'char_count': chunk.get('metadata', {}).get('char_count', 0)
                }
                
                # Add to section-level hash mapping
                self.hash_to_documents[content_hash].append(chunk_ref)
                self.document_to_hashes[document_name].add(content_hash)
                
                # Process sentence-level hashes
                sentence_hashes = chunk.get('sentence_hashes', [])
                for sentence_data in sentence_hashes:
                    sentence_hash = sentence_data.get('sentence_hash')
                    if sentence_hash:
                        # Create sentence reference
                        sentence_ref = {
                            'document_name': document_name,
                            'chunk_index': chunk.get('metadata', {}).get('chunk_index', 0),
                            'section_number': chunk.get('metadata', {}).get('section_number', 'unknown'),
                            'section_title': chunk.get('metadata', {}).get('section_title', 'unknown'),
                            'sentence_index': sentence_data.get('sentence_index', 0),
                            'sentence_text': sentence_data.get('sentence_text', ''),
                            'word_count': sentence_data.get('word_count', 0)
                        }
                        
                        # Add to sentence hash mapping
                        self.sentence_hash_to_documents[sentence_hash].append(sentence_ref)
                        self.document_to_sentence_hashes[document_name].add(sentence_hash)
            
            logger.info(f"Added {len(chunks)} chunks with sentence-level hashes from '{document_name}' to exact match index")
            
            # Save data to persistence file
            self._save_data()
            
        except Exception as e:
            logger.error(f"Error adding document chunks to exact match index: {str(e)}")
    
    def find_exact_matches(self, document_name: str) -> Dict[str, Any]:
        """
        Find exact matches for a specific document
        
        Args:
            document_name: Name of the document to analyze
            
        Returns:
            Dictionary with exact match analysis
        """
        try:
            if document_name not in self.document_to_hashes:
                return {"error": "Document not found", "matches": []}
            
            document_hashes = self.document_to_hashes[document_name]
            matches = []
            
            for content_hash in document_hashes:
                hash_documents = self.hash_to_documents[content_hash]
                
                # If more than one document has this hash, it's a match
                if len(hash_documents) > 1:
                    # Find other documents with this hash
                    other_docs = [doc for doc in hash_documents if doc['document_name'] != document_name]
                    
                    if other_docs:
                        match_info = {
                            'content_hash': content_hash,
                            'matching_documents': other_docs,
                            'total_matches': len(hash_documents),
                            'section_info': next((doc for doc in hash_documents if doc['document_name'] == document_name), None)
                        }
                        matches.append(match_info)
            
            return {
                "document": document_name,
                "total_unique_sections": len(document_hashes),
                "exact_matches": len(matches),
                "matches": matches
            }
            
        except Exception as e:
            logger.error(f"Error finding exact matches: {str(e)}")
            return {"error": str(e), "matches": []}
    
    def find_duplicate_sections(self) -> Dict[str, Any]:
        """
        Find all duplicate sections across all documents
        
        Returns:
            Dictionary with duplicate analysis
        """
        try:
            duplicates = []
            processed_hashes = set()
            
            for content_hash, documents in self.hash_to_documents.items():
                if len(documents) > 1 and content_hash not in processed_hashes:
                    # This is a duplicate section
                    duplicate_info = {
                        'content_hash': content_hash,
                        'duplicate_count': len(documents),
                        'documents': documents,
                        'section_preview': documents[0]['text_preview']
                    }
                    duplicates.append(duplicate_info)
                    processed_hashes.add(content_hash)
            
            # Calculate statistics
            total_duplicates = len(duplicates)
            total_documents = len(self.document_to_hashes)
            
            return {
                "total_duplicate_sections": total_duplicates,
                "total_documents": total_documents,
                "duplicates": duplicates,
                "summary": f"Found {total_duplicates} duplicate sections across {total_documents} documents"
            }
            
        except Exception as e:
            logger.error(f"Error finding duplicate sections: {str(e)}")
            return {"error": str(e), "duplicates": []}
    
    def compare_documents_sentence_level(self, doc1_name: str, doc2_name: str) -> Dict[str, Any]:
        """
        Compare two documents for exact sentence matches
        
        Args:
            doc1_name: First document name
            doc2_name: Second document name
            
        Returns:
            Dictionary with sentence-level comparison results
        """
        try:
            if doc1_name not in self.document_to_sentence_hashes or doc2_name not in self.document_to_sentence_hashes:
                return {"error": "One or both documents not found"}
            
            doc1_sentence_hashes = self.document_to_sentence_hashes[doc1_name]
            doc2_sentence_hashes = self.document_to_sentence_hashes[doc2_name]
            
            # Find common sentence hashes
            common_sentence_hashes = doc1_sentence_hashes.intersection(doc2_sentence_hashes)
            
            # Get detailed sentence match information
            sentence_matches = []
            for sentence_hash in common_sentence_hashes:
                sentence_documents = self.sentence_hash_to_documents[sentence_hash]
                doc1_match = next((doc for doc in sentence_documents if doc['document_name'] == doc1_name), None)
                doc2_match = next((doc for doc in sentence_documents if doc['document_name'] == doc2_name), None)
                
                if doc1_match and doc2_match:
                    sentence_matches.append({
                        'sentence_hash': sentence_hash,
                        'doc1_sentence': doc1_match,
                        'doc2_sentence': doc2_match,
                        'matched_sentence': doc1_match.get('sentence_text', ''),  # Actual sentence content
                        'section_title': doc1_match.get('section_title', ''),
                        'section_number': doc1_match.get('section_number', ''),
                        'sentence_index': doc1_match.get('sentence_index', 0)
                    })
            
            # Calculate sentence-level similarity metrics
            doc1_total_sentences = len(doc1_sentence_hashes)
            doc2_total_sentences = len(doc2_sentence_hashes)
            common_sentences = len(common_sentence_hashes)
            
            sentence_similarity_score = (common_sentences * 2) / (doc1_total_sentences + doc2_total_sentences) if (doc1_total_sentences + doc2_total_sentences) > 0 else 0
            
            return {
                "doc1": doc1_name,
                "doc2": doc2_name,
                "doc1_total_sentences": doc1_total_sentences,
                "doc2_total_sentences": doc2_total_sentences,
                "common_sentences": common_sentences,
                "sentence_match_score": sentence_similarity_score,
                "sentence_matches": sentence_matches
            }
            
        except Exception as e:
            logger.error(f"Error comparing documents at sentence level: {str(e)}")
            return {"error": str(e)}
    
    def get_document_differences(self, doc1_name: str, doc2_name: str) -> Dict[str, Any]:
        """
        Get actual differences (non-matching content) between two documents
        
        Args:
            doc1_name: First document name
            doc2_name: Second document name
            
        Returns:
            Dictionary with actual differences
        """
        try:
            if doc1_name not in self.document_to_hashes or doc2_name not in self.document_to_hashes:
                return {"error": "One or both documents not found"}
            
            doc1_hashes = self.document_to_hashes[doc1_name]
            doc2_hashes = self.document_to_hashes[doc2_name]
            
            # Find differences (content unique to each document)
            doc1_unique = doc1_hashes - doc2_hashes
            doc2_unique = doc2_hashes - doc1_hashes
            
            # Get actual content for differences
            doc1_differences = []
            for content_hash in doc1_unique:
                hash_documents = self.hash_to_documents[content_hash]
                doc1_match = next((doc for doc in hash_documents if doc['document_name'] == doc1_name), None)
                if doc1_match:
                    doc1_differences.append({
                        'content_hash': content_hash,
                        'content': doc1_match.get('content', ''),
                        'section_title': doc1_match.get('section_title', ''),
                        'section_number': doc1_match.get('section_number', ''),
                        'char_count': doc1_match.get('char_count', 0),
                        'word_count': doc1_match.get('word_count', 0)
                    })
            
            doc2_differences = []
            for content_hash in doc2_unique:
                hash_documents = self.hash_to_documents[content_hash]
                doc2_match = next((doc for doc in hash_documents if doc['document_name'] == doc2_name), None)
                if doc2_match:
                    doc2_differences.append({
                        'content_hash': content_hash,
                        'content': doc2_match.get('content', ''),
                        'section_title': doc2_match.get('section_title', ''),
                        'section_number': doc2_match.get('section_number', ''),
                        'char_count': doc2_match.get('char_count', 0),
                        'word_count': doc2_match.get('word_count', 0)
                    })
            
            return {
                "doc1": doc1_name,
                "doc2": doc2_name,
                "doc1_unique_sections": doc1_differences,
                "doc2_unique_sections": doc2_differences,
                "doc1_unique_count": len(doc1_differences),
                "doc2_unique_count": len(doc2_differences)
            }
            
        except Exception as e:
            logger.error(f"Error getting document differences: {str(e)}")
            return {"error": str(e)}
    
    def compare_documents_exact(self, doc1_name: str, doc2_name: str) -> Dict[str, Any]:
        """
        Compare two documents for exact matches
        
        Args:
            doc1_name: First document name
            doc2_name: Second document name
            
        Returns:
            Dictionary with comparison results
        """
        try:
            if doc1_name not in self.document_to_hashes or doc2_name not in self.document_to_hashes:
                return {"error": "One or both documents not found"}
            
            doc1_hashes = self.document_to_hashes[doc1_name]
            doc2_hashes = self.document_to_hashes[doc2_name]
            
            # Find common hashes
            common_hashes = doc1_hashes.intersection(doc2_hashes)
            
            # Get detailed match information with actual content
            matches = []
            for content_hash in common_hashes:
                hash_documents = self.hash_to_documents[content_hash]
                doc1_match = next((doc for doc in hash_documents if doc['document_name'] == doc1_name), None)
                doc2_match = next((doc for doc in hash_documents if doc['document_name'] == doc2_name), None)
                
                if doc1_match and doc2_match:
                    matches.append({
                        'content_hash': content_hash,
                        'doc1_section': doc1_match,
                        'doc2_section': doc2_match,
                        'matched_content': doc1_match.get('content', ''),  # Actual text content
                        'section_title': doc1_match.get('section_title', ''),
                        'section_number': doc1_match.get('section_number', ''),
                        'char_count': doc1_match.get('char_count', 0),
                        'word_count': doc1_match.get('word_count', 0)
                    })
            
            # Calculate similarity metrics
            doc1_total = len(doc1_hashes)
            doc2_total = len(doc2_hashes)
            common_total = len(common_hashes)
            
            similarity_score = (common_total * 2) / (doc1_total + doc2_total) if (doc1_total + doc2_total) > 0 else 0
            
            return {
                "doc1": doc1_name,
                "doc2": doc2_name,
                "doc1_total_sections": doc1_total,
                "doc2_total_sections": doc2_total,
                "common_sections": common_total,
                "exact_match_score": similarity_score,
                "matches": matches
            }
            
        except Exception as e:
            logger.error(f"Error comparing documents: {str(e)}")
            return {"error": str(e)}
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about stored documents and hashes"""
        try:
            total_documents = len(self.document_to_hashes)
            total_hashes = len(self.hash_to_documents)
            
            # Count unique vs duplicate hashes
            unique_hashes = sum(1 for docs in self.hash_to_documents.values() if len(docs) == 1)
            duplicate_hashes = sum(1 for docs in self.hash_to_documents.values() if len(docs) > 1)
            
            return {
                "total_documents": total_documents,
                "total_unique_sections": total_hashes,
                "unique_content_hashes": unique_hashes,
                "duplicate_content_hashes": duplicate_hashes,
                "documents": list(self.document_to_hashes.keys())
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            return {"error": str(e)}
    
    def remove_document(self, document_name: str) -> int:
        """
        Remove a document from the exact match index
        
        Args:
            document_name: Name of document to remove
            
        Returns:
            Number of chunks removed
        """
        try:
            if document_name not in self.document_to_hashes:
                return 0
            
            document_hashes = self.document_to_hashes[document_name]
            removed_count = 0
            
            # Remove from hash mappings
            for content_hash in document_hashes:
                if content_hash in self.hash_to_documents:
                    # Remove this document's entries
                    original_docs = self.hash_to_documents[content_hash]
                    self.hash_to_documents[content_hash] = [
                        doc for doc in original_docs if doc['document_name'] != document_name
                    ]
                    
                    # If no documents left for this hash, remove it
                    if not self.hash_to_documents[content_hash]:
                        del self.hash_to_documents[content_hash]
                    
                    removed_count += 1
            
            # Remove from document mapping
            del self.document_to_hashes[document_name]
            
            logger.info(f"Removed {removed_count} chunks for document '{document_name}' from exact match index")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error removing document: {str(e)}")
            return 0
    
    def _load_data(self):
        """Load data from persistence file"""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)
                
                # Convert back to defaultdicts and sets
                self.hash_to_documents = defaultdict(list, data.get('hash_to_documents', {}))
                self.sentence_hash_to_documents = defaultdict(list, data.get('sentence_hash_to_documents', {}))
                
                # Convert sets back from lists
                self.document_to_hashes = defaultdict(set)
                for doc, hashes in data.get('document_to_hashes', {}).items():
                    self.document_to_hashes[doc] = set(hashes)
                
                self.document_to_sentence_hashes = defaultdict(set)
                for doc, hashes in data.get('document_to_sentence_hashes', {}).items():
                    self.document_to_sentence_hashes[doc] = set(hashes)
                
                logger.info(f"Loaded exact match data from {self.persistence_file}")
            else:
                logger.info("No existing exact match data found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading exact match data: {str(e)}")
            # Continue with empty data
    
    def _save_data(self):
        """Save data to persistence file"""
        try:
            # Convert sets to lists for JSON serialization
            data = {
                'hash_to_documents': dict(self.hash_to_documents),
                'sentence_hash_to_documents': dict(self.sentence_hash_to_documents),
                'document_to_hashes': {doc: list(hashes) for doc, hashes in self.document_to_hashes.items()},
                'document_to_sentence_hashes': {doc: list(hashes) for doc, hashes in self.document_to_sentence_hashes.items()}
            }
            
            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved exact match data to {self.persistence_file}")
        except Exception as e:
            logger.error(f"Error saving exact match data: {str(e)}")
