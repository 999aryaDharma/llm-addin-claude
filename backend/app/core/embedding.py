"""
Embedding module using Hugging Face sentence-transformers/all-MiniLM-L6-v2
"""
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from typing import List
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Wrapper for Hugging Face embedding operations"""
    
    def __init__(self):
        """Initialize Hugging Face embeddings with MiniLM"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL
            )
            logger.info(f"Initialized HF embeddings with model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = await self.embeddings.aembed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = await self.embeddings.aembed_documents(texts)
            logger.info(f"Generated embeddings for {len(texts)} documents")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise
    
    def get_embeddings_instance(self) -> Embeddings:
        """
        Get the embeddings instance for use with LangChain
        
        Returns:
            LangChain Embeddings object
        """
        return self.embeddings
    
    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Embed texts in batches for large datasets
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
            
        Returns:
            List of all embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        return all_embeddings


# Global instance
embedding_service = EmbeddingService()