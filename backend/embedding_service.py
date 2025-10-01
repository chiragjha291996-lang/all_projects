import os
import logging
import re
from typing import List, Dict, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import json
from section_chunker import SectionChunker

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for processing documents using section-based embeddings"""
    
    def __init__(self):
        # Use a lightweight but effective model for embeddings
        self.model_name = "all-MiniLM-L6-v2"  # Fast and good quality
        self.model = SentenceTransformer(self.model_name)
        
        # Initialize section-based chunker
        self.section_chunker = SectionChunker()
        
        # Fallback chunking parameters (for documents without clear sections)
        self.chunk_size = 500  # Characters per chunk
        self.chunk_overlap = 100  # Overlap between chunks
        self.min_chunk_size = 50  # Minimum chunk size
        
        logger.info(f"Initialized embedding service with model: {self.model_name} and section-based chunking")
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return np.array([])
    
    def create_chunks_with_embeddings(self, text_content: str, filename: str) -> List[Dict]:
        """
        Main method to create chunks with embeddings - tries section-based first
        
        Args:
            text_content: Full text content of the document
            filename: Name of the source file
            
        Returns:
            List of chunk dictionaries with text, embeddings, and metadata
        """
        try:
            if not text_content or len(text_content.strip()) < self.min_chunk_size:
                logger.warning(f"Document too short for chunking: {filename}")
                return []
            
            # Try section-based chunking first
            section_chunks = self.section_chunker.create_section_chunks(text_content, filename)
            
            if not section_chunks:
                logger.warning(f"No sections detected, falling back to size-based chunking for {filename}")
                return self._create_fallback_chunks(text_content, filename)
            
            # Generate embeddings for section chunks
            chunk_texts = [chunk['text'] for chunk in section_chunks]
            embeddings = self.model.encode(chunk_texts, convert_to_numpy=True)
            
            # Add embeddings to chunks
            for i, chunk in enumerate(section_chunks):
                chunk['embedding'] = embeddings[i].tolist()
                chunk['metadata']['embedding_model'] = self.model_name
                chunk['metadata']['global_chunk_id'] = i
                chunk['metadata']['chunk_id'] = f"{filename}_{i}"
            
            logger.info(f"Successfully created {len(section_chunks)} section-based chunks for {filename}")
            return section_chunks
            
        except Exception as e:
            logger.error(f"Error in section-based chunking for {filename}: {str(e)}")
            logger.info(f"Falling back to size-based chunking for {filename}")
            return self._create_fallback_chunks(text_content, filename)
    
    def _create_fallback_chunks(self, text_content: str, filename: str) -> List[Dict]:
        """
        Fallback to size-based chunking when sections can't be detected
        """
        try:
            # Clean text
            cleaned_text = text_content.strip()
            
            # If text is small enough, create single chunk
            if len(cleaned_text) <= self.chunk_size:
                chunk = {
                    'text': cleaned_text,
                    'metadata': {
                        'start_char': 0,
                        'end_char': len(cleaned_text),
                        'char_count': len(cleaned_text),
                        'word_count': len(cleaned_text.split()),
                        'chunk_index': 0,
                        'chunk_type': 'size_based_fallback',
                        'filename': filename,
                        'embedding_model': self.model_name,
                        'global_chunk_id': 0,
                        'chunk_id': f"{filename}_0"
                    }
                }
                
                # Generate embedding
                embedding = self.model.encode([cleaned_text], convert_to_numpy=True)
                chunk['embedding'] = embedding[0].tolist()
                
                return [chunk]
            
            # Create multiple chunks using sliding window approach
            chunks = []
            start = 0
            chunk_index = 0
            
            while start < len(cleaned_text):
                # Determine end position
                end = min(start + self.chunk_size, len(cleaned_text))
                
                # Try to break at sentence boundary if possible
                if end < len(cleaned_text):
                    # Look for sentence end within overlap range
                    break_point = cleaned_text.rfind('.', start, end - self.chunk_overlap)
                    if break_point > start:
                        end = break_point + 1
                
                chunk_text = cleaned_text[start:end].strip()
                
                if len(chunk_text) >= self.min_chunk_size:
                    chunk = {
                        'text': chunk_text,
                        'metadata': {
                            'start_char': start,
                            'end_char': end,
                            'char_count': len(chunk_text),
                            'word_count': len(chunk_text.split()),
                            'chunk_index': chunk_index,
                            'chunk_type': 'size_based_fallback',
                            'filename': filename,
                            'embedding_model': self.model_name,
                            'global_chunk_id': chunk_index,
                            'chunk_id': f"{filename}_{chunk_index}"
                        }
                    }
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Move start position for next chunk
                start = end - self.chunk_overlap
                if start >= len(cleaned_text):
                    break
            
            # Generate embeddings for all chunks
            if chunks:
                chunk_texts = [chunk['text'] for chunk in chunks]
                embeddings = self.model.encode(chunk_texts, convert_to_numpy=True)
                
                for i, chunk in enumerate(chunks):
                    chunk['embedding'] = embeddings[i].tolist()
            
            logger.info(f"Created {len(chunks)} fallback chunks for {filename}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error in fallback chunking for {filename}: {str(e)}")
            return []
    
    def get_document_structure(self, chunks: List[Dict]) -> Dict:
        """
        Get hierarchical structure information from section-based chunks
        """
        try:
            return self.section_chunker.get_section_hierarchy(chunks)
        except Exception as e:
            logger.error(f"Error getting document structure: {str(e)}")
            return {"error": "Could not determine document structure"}
    
    def calculate_similarity(self, chunks1: List[Dict], chunks2: List[Dict]) -> Dict:
        """
        Calculate similarity between two sets of chunks
        """
        try:
            if not chunks1 or not chunks2:
                return {"similarity_score": 0.0, "error": "Empty chunk sets"}
            
            # Get embeddings
            embeddings1 = np.array([chunk['embedding'] for chunk in chunks1])
            embeddings2 = np.array([chunk['embedding'] for chunk in chunks2])
            
            # Calculate average embeddings for each document
            avg_embedding1 = np.mean(embeddings1, axis=0)
            avg_embedding2 = np.mean(embeddings2, axis=0)
            
            # Calculate cosine similarity
            similarity = cosine_similarity([avg_embedding1], [avg_embedding2])[0][0]
            
            # Also calculate chunk-level similarities for detailed analysis
            chunk_similarities = []
            for i, emb1 in enumerate(embeddings1):
                for j, emb2 in enumerate(embeddings2):
                    sim = cosine_similarity([emb1], [emb2])[0][0]
                    chunk_similarities.append({
                        'chunk1_index': i,
                        'chunk2_index': j,
                        'similarity': float(sim),
                        'chunk1_section': chunks1[i]['metadata'].get('section_title', 'Unknown'),
                        'chunk2_section': chunks2[j]['metadata'].get('section_title', 'Unknown')
                    })
            
            # Sort by similarity score
            chunk_similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                "similarity_score": float(similarity),
                "chunk_count_1": len(chunks1),
                "chunk_count_2": len(chunks2),
                "top_similar_chunks": chunk_similarities[:10],  # Top 10 most similar chunk pairs
                "avg_chunk_similarity": float(np.mean([cs['similarity'] for cs in chunk_similarities]))
            }
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return {"similarity_score": 0.0, "error": str(e)}
    
    def cluster_chunks(self, all_chunks: List[Dict], eps: float = 0.3, min_samples: int = 2) -> Dict:
        """
        Cluster chunks using DBSCAN based on their embeddings
        """
        try:
            if len(all_chunks) < 2:
                return {"clusters": [], "noise_points": [], "cluster_count": 0}
            
            # Get embeddings
            embeddings = np.array([chunk['embedding'] for chunk in all_chunks])
            
            # Perform clustering
            clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
            cluster_labels = clustering.fit_predict(embeddings)
            
            # Organize results
            clusters = {}
            noise_points = []
            
            for i, label in enumerate(cluster_labels):
                chunk_info = {
                    'chunk_index': i,
                    'text_preview': all_chunks[i]['text'][:100] + "..." if len(all_chunks[i]['text']) > 100 else all_chunks[i]['text'],
                    'section_title': all_chunks[i]['metadata'].get('section_title', 'Unknown'),
                    'filename': all_chunks[i]['metadata'].get('filename', 'Unknown')
                }
                
                if label == -1:  # Noise point
                    noise_points.append(chunk_info)
                else:
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(chunk_info)
            
            return {
                "clusters": [{"cluster_id": k, "chunks": v} for k, v in clusters.items()],
                "noise_points": noise_points,
                "cluster_count": len(clusters)
            }
            
        except Exception as e:
            logger.error(f"Error clustering chunks: {str(e)}")
            return {"clusters": [], "noise_points": [], "cluster_count": 0, "error": str(e)}
