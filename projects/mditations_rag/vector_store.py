import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
import logging
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Manages ChromaDB vector database operations for RAG system."""
    
    def __init__(self, collection_name: str = "meditations", persist_directory: str = "./chroma_db"):
        """Initialize vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection.
            persist_directory: Directory to persist the database.
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize better sentence transformer for embeddings
        # all-mpnet-base-v2 is better than all-MiniLM-L6-v2 for semantic search
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info(f"Vector store initialized with all-mpnet-base-v2: {collection_name}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Meditations by Marcus Aurelius"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store.
        
        Args:
            documents: List of documents with 'content' and 'metadata' keys.
        """
        try:
            contents = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            ids = [f"chunk_{i}" for i in range(len(documents))]
            
            # Generate embeddings with better model
            embeddings = self.embedding_model.encode(contents).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query: Search query string.
            n_results: Number of results to return.
            
        Returns:
            List of similar documents with scores.
        """
        try:
            # Generate query embedding with better model
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Defensive: Check if results are valid and contain expected keys
            if (
                not results
                or "documents" not in results
                or not results["documents"]
                or not results["documents"][0]
            ):
                logger.warning("No results found in vector store search.")
                return []
            
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "id": results["ids"][0][i]
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection.
        
        Returns:
            Dictionary with collection statistics.
        """
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_model": "all-mpnet-base-v2"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            self.collection.delete(where={})
            logger.info("Cleared all documents from collection")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

if __name__ == "__main__":
    # Test the vector store
    vector_store = VectorStore()
    info = vector_store.get_collection_info()
    print(f"Collection info: {info}") 