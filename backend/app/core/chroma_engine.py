"""
ChromaDB engine for vector storage and retrieval
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from app.config import settings
from app.core.embedding import embedding_service

logger = logging.getLogger(__name__)


class ChromaEngine:
    """ChromaDB operations for document storage and retrieval"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Office documents vector store"}
            )
            
            logger.info(f"ChromaDB initialized at {settings.CHROMA_DB_PATH}")
            logger.info(f"Collection '{settings.CHROMA_COLLECTION_NAME}' has {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    async def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to ChromaDB with embeddings
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata for each chunk
            ids: Optional list of IDs (generated if not provided)
            
        Returns:
            Success status
        """
        try:
            # Generate embeddings using our embedding service
            embeddings = await embedding_service.embed_documents(texts)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}_{hash(text)}" for i, text in enumerate(texts)]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} documents to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise
    
    async def query_similar(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query similar documents using semantic search
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            Query results with documents, distances, and metadata
        """
        try:
            # Generate query embedding
            query_embedding = await embedding_service.embed_text(query_text)
            
            # Query collection
            # Handle ChromaDB filter format - check if multiple conditions need special operator
            if filter_metadata and len(filter_metadata) > 1:
                # For multiple conditions, use $and operator if required by ChromaDB version
                where_clause = {"$and": [{key: value} for key, value in filter_metadata.items()]}
            elif filter_metadata:
                # For single condition, use direct format
                where_clause = filter_metadata
            else:
                where_clause = None
                
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause
            )
            
            logger.info(f"Found {len(results['documents'][0])} similar documents")
            
            return {
                "documents": results["documents"][0],
                "distances": results["distances"][0],
                "metadatas": results["metadatas"][0],
                "ids": results["ids"][0]
            }
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            Success status
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    def delete_by_metadata(self, filter_metadata: Dict[str, Any]) -> bool:
        """
        Delete documents by metadata filter
        
        Args:
            filter_metadata: Metadata filter
            
        Returns:
            Success status
        """
        try:
            self.collection.delete(where=filter_metadata)
            logger.info(f"Deleted documents matching filter: {filter_metadata}")
            return True
        except Exception as e:
            logger.error(f"Error deleting by metadata: {str(e)}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None
        """
        try:
            result = self.collection.get(ids=[doc_id])
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return None
    
    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List documents with pagination
        
        Args:
            limit: Maximum number of documents
            offset: Offset for pagination
            filter_metadata: Optional metadata filter
            
        Returns:
            List of documents with metadata
        """
        try:
            result = self.collection.get(
                where=filter_metadata,
                limit=limit,
                offset=offset
            )
            
            return {
                "count": len(result["ids"]),
                "documents": result["documents"],
                "metadatas": result["metadatas"],
                "ids": result["ids"]
            }
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics
        
        Returns:
            Collection statistics
        """
        try:
            count = self.collection.count()
            
            return {
                "name": settings.CHROMA_COLLECTION_NAME,
                "count": count,
                "path": settings.CHROMA_DB_PATH
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise
    
    def reset_collection(self) -> bool:
        """
        Reset/clear the entire collection
        
        Returns:
            Success status
        """
        try:
            self.client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Office documents vector store"}
            )
            logger.warning(f"Collection '{settings.CHROMA_COLLECTION_NAME}' has been reset")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise
    
    async def update_document(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update an existing document
        
        Args:
            doc_id: Document ID
            text: New text content
            metadata: New metadata
            
        Returns:
            Success status
        """
        try:
            # Generate new embedding
            embedding = await embedding_service.embed_text(text)
            
            # Update in collection
            self.collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )
            
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise


# Global instance
chroma_engine = ChromaEngine()