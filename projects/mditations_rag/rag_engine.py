import os
from typing import List, Dict, Any, Optional
import logging
import requests
import json
from dotenv import load_dotenv

from vector_store import VectorStore

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Commented out GeminiChunkingError and Gemini code
# class GeminiChunkingError(Exception):
#     def __init__(self, message, stage=None):
#         super().__init__(message)
#         self.stage = stage

class RAGEngine:
    """Core RAG engine that combines retrieval and generation using OpenRouter's kimi-k2 model."""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store if vector_store is not None else VectorStore()
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        logger.info("RAG engine initialized with OpenRouter kimi-k2 model")
    
    def retrieve_relevant_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.vector_store.search(query, n_results=n_results)
            logger.info(f"Retrieved {len(results)} relevant passages")
            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            raise Exception(f"Error retrieving context: {e}")
    
    def generate_response(self, query: str, context: List[Dict[str, Any]], model: str = "moonshotai/kimi-k2:free") -> str:
        try:
            context_text = "\n\n".join([
                f"Passage {i+1}:\n{doc['content']}"
                for i, doc in enumerate(context)
            ])
            system_prompt = "You are an expert on Marcus Aurelius's 'Meditations'. Provide concise, direct answers (4-5 sentences maximum) based on the provided passages. Always include at least one direct quotation from the text to support your answer. Use quotation marks for direct quotes. Be precise and avoid lengthy explanations."
            user_prompt = f"Question: {query}\n\nRelevant passages from Meditations:\n{context_text}\n\nProvide a concise answer (4-5 sentences) with at least one direct quotation from the text:"
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": messages
            }
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                logger.info("Generated response with %s", model)
                return answer
            else:
                logger.error(f"OpenRouter API error: {response.status_code} {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Unexpected error in generate_response: {e}")
            raise Exception(f"Error generating response: {e}")
    
    def answer_question(self, query: str, n_context: int = 5, model: str = "moonshotai/kimi-k2:free") -> Dict[str, Any]:
        try:
            logger.info(f"Processing question: {query}")
            context = self.retrieve_relevant_context(query, n_context)
            answer = self.generate_response(query, context, model=model)
            result = {
                "question": query,
                "answer": answer,
                "context": context,
                "num_context_passages": len(context)
            }
            logger.info("RAG pipeline completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            raise
    
    def get_system_info(self) -> Dict[str, Any]:
        try:
            vector_store_info = self.vector_store.get_collection_info()
            return {
                "vector_store": vector_store_info,
                "model": "moonshotai/kimi-k2:free",
                "status": "ready"
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            raise

if __name__ == "__main__":
    rag_engine = RAGEngine()
    try:
        info = rag_engine.get_system_info()
        print(f"RAG system info: {info}")
    except Exception as e:
        print(f"Error during system info retrieval: {e}") 