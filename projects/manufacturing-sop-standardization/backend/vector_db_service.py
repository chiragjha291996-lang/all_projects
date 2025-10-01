import os
import logging
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorDBService:
    """Simplified service for storing document chunks in a vector database using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the vector database service"""
        self.persist_directory = persist_directory
        self.base_collection_name = "sop_documents"
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model (same as embedding_service for consistency)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Track document collections
        self.document_collections = {}
        
        logger.info(f"Initialized VectorDB service with persistence at: {persist_directory}")
    
    def _get_or_create_document_collection(self, document_name: str):
        """Get or create a collection for a specific document"""
        # Create a safe collection name that meets ChromaDB requirements:
        # 1. 3-63 characters
        # 2. Start and end with alphanumeric
        # 3. Only alphanumeric, underscores, hyphens
        # 4. No consecutive periods
        # 5. Not a valid IPv4 address
        
        # Remove file extension and sanitize
        base_name = os.path.splitext(document_name)[0]
        
        # Replace invalid characters with underscores
        safe_name = base_name.replace(' ', '_').replace('-', '_').replace('.', '_')
        
        # Remove consecutive underscores
        while '__' in safe_name:
            safe_name = safe_name.replace('__', '_')
        
        # Ensure it starts and ends with alphanumeric
        safe_name = safe_name.strip('_')
        if not safe_name[0].isalnum():
            safe_name = 'doc_' + safe_name
        if not safe_name[-1].isalnum():
            safe_name = safe_name + '_doc'
        
        # Truncate if too long (leave room for base prefix)
        max_safe_length = 50  # Leave room for "sop_documents_" prefix
        if len(safe_name) > max_safe_length:
            safe_name = safe_name[:max_safe_length].rstrip('_')
        
        # Create final collection name
        collection_name = f"{self.base_collection_name}_{safe_name}"
        
        # Final validation - ensure it meets all requirements
        if len(collection_name) > 63:
            # Use hash-based naming for very long names
            import hashlib
            name_hash = hashlib.md5(document_name.encode()).hexdigest()[:8]
            collection_name = f"{self.base_collection_name}_{name_hash}"
        
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection '{collection_name}' with {collection.count()} chunks")
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "description": f"SOP document chunks for {document_name}",
                    "source_document": document_name
                }
            )
            logger.info(f"Created new collection '{collection_name}' for document '{document_name}'")
        
        # Cache the collection
        self.document_collections[document_name] = collection
        return collection
    
    def add_document_chunks(self, document_name: str, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Add document chunks to the vector database
        
        Args:
            document_name: Name of the source document
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            
        Returns:
            List of chunk IDs that were added
        """
        try:
            # Get or create collection for this specific document
            collection = self._get_or_create_document_collection(document_name)
            
            chunk_ids = []
            texts = []
            metadatas = []
            embeddings = []
            
            for i, chunk in enumerate(chunks):
                # Generate unique ID for each chunk
                chunk_id = f"{document_name}_{i}_{str(uuid.uuid4())[:8]}"
                chunk_ids.append(chunk_id)
                
                # Extract text content
                chunk_text = chunk.get('text', '')
                texts.append(chunk_text)
                
                # Prepare metadata - filter out None values for ChromaDB compatibility
                chunk_metadata = chunk.get('metadata', {})
                
                # Filter out None values and convert to ChromaDB-compatible types
                filtered_metadata = {}
                for key, value in chunk_metadata.items():
                    if value is not None:
                        # Convert to ChromaDB-compatible types
                        if isinstance(value, (str, int, float, bool)):
                            filtered_metadata[key] = value
                        elif isinstance(value, list):
                            # Convert lists to strings for ChromaDB
                            filtered_metadata[key] = str(value)
                        else:
                            # Convert other types to strings
                            filtered_metadata[key] = str(value)
                
                metadata = {
                    'document_name': document_name,
                    'chunk_index': i,
                    'char_count': len(chunk_text),
                    'word_count': len(chunk_text.split()) if chunk_text else 0,
                    **filtered_metadata
                }
                metadatas.append(metadata)
                
                # Generate embedding for the chunk
                embedding = self.embedding_model.encode(chunk_text).tolist()
                embeddings.append(embedding)
            
            # Add all chunks to the document-specific collection in batch
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=chunk_ids,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(chunk_ids)} chunks from document '{document_name}' to document-specific collection")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Failed to add document chunks to vector database: {str(e)}")
            raise
    
    def get_document_chunks(self, document_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific document
        
        Args:
            document_name: Name of the document
            
        Returns:
            List of chunk dictionaries
        """
        try:
            # Get the document-specific collection
            collection = self._get_or_create_document_collection(document_name)
            
            results = collection.get(
                include=['documents', 'metadatas']
            )
            
            chunks = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    chunk = {
                        'id': results['ids'][i],
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    chunks.append(chunk)
            
            # Sort by chunk_index if available
            chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
            
            logger.info(f"Retrieved {len(chunks)} chunks for document '{document_name}' from dedicated collection")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to get document chunks: {str(e)}")
            raise
    
    def delete_document(self, document_name: str) -> int:
        """
        Delete all chunks for a specific document
        
        Args:
            document_name: Name of the document to delete
            
        Returns:
            Number of chunks deleted
        """
        try:
            # Get the document-specific collection
            collection = self._get_or_create_document_collection(document_name)
            
            # Get all chunk IDs from the collection
            results = collection.get(include=['metadatas'])
            
            if results['ids']:
                # Delete all chunks from the document-specific collection
                collection.delete(ids=results['ids'])
                deleted_count = len(results['ids'])
                logger.info(f"Deleted {deleted_count} chunks for document '{document_name}' from dedicated collection")
                return deleted_count
            else:
                logger.info(f"No chunks found for document '{document_name}'")
                return 0
                
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all document collections"""
        try:
            # Get all collections
            all_collections = self.client.list_collections()
            sop_collections = [col for col in all_collections if col.name.startswith(self.base_collection_name)]
            
            total_chunks = 0
            document_counts = {}
            
            for collection_info in sop_collections:
                collection = self.client.get_collection(name=collection_info.name)
                chunk_count = collection.count()
                total_chunks += chunk_count
                
                # Extract document name from collection name
                doc_name = collection_info.name.replace(f"{self.base_collection_name}_", "")
                document_counts[doc_name] = chunk_count
            
            stats = {
                'total_chunks': total_chunks,
                'total_documents': len(document_counts),
                'document_chunk_counts': document_counts,
                'base_collection_name': self.base_collection_name,
                'persist_directory': self.persist_directory,
                'collections': [col.name for col in sop_collections]
            }
            
            logger.info(f"Collection stats: {total_chunks} chunks across {len(document_counts)} documents in {len(sop_collections)} collections")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            raise
    
    def list_documents(self) -> List[str]:
        """
        Get list of all document names in the vector database
        
        Returns:
            List of document names
        """
        try:
            # Get all collections
            all_collections = self.client.list_collections()
            sop_collections = [col for col in all_collections if col.name.startswith(self.base_collection_name)]
            
            document_names = []
            for collection_info in sop_collections:
                # Extract document name from collection name
                doc_name = collection_info.name.replace(f"{self.base_collection_name}_", "")
                document_names.append(doc_name)
            
            logger.info(f"Found {len(document_names)} documents in vector database")
            return document_names
            
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            raise