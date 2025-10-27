"""
Query endpoints for Word document operations
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging

from app.models.query import QueryRequest, QueryResponse, ContextRequest
from app.models.document import DocumentSearchRequest
from app.core.chroma_engine import chroma_engine
from app.core.cache_manager import cache_manager
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search", response_model=QueryResponse)
async def semantic_search(request: QueryRequest):
    """
    Semantic search in Word documents using RAG
    """
    try:
        # Check cache first
        cache_key = f"search_{request.query}_{request.document_id}"
        cached = cache_manager.get(cache_key)
        
        if cached and not request.bypass_cache:
            logger.info(f"Cache hit for query: {request.query}")
            return QueryResponse(**cached)
        
        # Build filter
        filter_metadata = {}
        if request.document_id:
            filter_metadata["document_id"] = request.document_id
        else:
            # Only filter by document_type if no specific document is requested
            filter_metadata["document_type"] = "word"
        
        # Search ChromaDB
        results = await chroma_engine.query_similar(
            query_text=request.query,
            n_results=request.max_results,
            filter_metadata=filter_metadata
        )
        
        # Check if results exist
        if not results["documents"] or len(results["documents"]) == 0 or all(not doc for doc in results["documents"]):
            # No relevant documents found - provide general response
            prompt = f"""The query "{request.query}" was searched in the document database but no relevant content was found.
            Please provide a helpful response based on general knowledge.
            
            Question: {request.query}
            
            Answer:"""
            
            answer = await llm_service.generate_text(prompt)
            
            response = QueryResponse(
                query=request.query,
                answer=answer,
                sources=[],
                relevance_scores=[],
                document_ids=[]
            )
        else:
            # Get context from multiple documents with chunk indexing
            documents_context = []
            all_sources = []
            all_relevance_scores = []
            all_document_ids = []
            
            # Combine content from multiple documents with chunk information
            for i, doc_content in enumerate(results["documents"]):
                if doc_content.strip():  # Only add non-empty documents
                    # Extract chunk information if available in metadata
                    chunk_info = ""
                    if "metadatas" in results and i < len(results["metadatas"]):
                        metadata = results["metadatas"][i]
                        chunk_idx = metadata.get("chunk_index", "unknown")
                        doc_id = metadata.get("document_id", "unknown")
                        chunk_info = f"[Document: {doc_id}, Chunk: {chunk_idx}]"
                    
                    doc_context = f"{chunk_info}\n{doc_content}\n"
                    documents_context.append(doc_context)
                    all_sources.append(doc_content)
                    all_relevance_scores.append(float(1 - results["distances"][i]))
                    if "metadatas" in results and i < len(results["metadatas"]):
                        metadata = results["metadatas"][i]
                        if "document_id" in metadata:
                            all_document_ids.append(metadata["document_id"])
            
            # Join all document contexts
            combined_context = "\n\n".join(documents_context)
            
            # Generate answer using LLM with chunk-aware context
            prompt = f"""Based on the following context from multiple documents and document chunks, answer the question.

Context:
{combined_context}

Question: {request.query}

Answer:"""
            
            answer = await llm_service.generate_text(prompt)
            
            response = QueryResponse(
                query=request.query,
                answer=answer,
                sources=all_sources,
                relevance_scores=all_relevance_scores,
                document_ids=all_document_ids
            )
        
        # Cache result
        cache_manager.set(cache_key, response.dict())
        
        return response
        
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a question that intelligently searches across documents and synthesizes answers
    """
    try:
        # Check cache first
        cache_key = f"ask_{request.query}_{request.document_id}"
        cached = cache_manager.get(cache_key)
        
        if cached and not request.bypass_cache:
            logger.info(f"Cache hit for ask: {request.query}")
            return QueryResponse(**cached)

        # If no specific document ID is requested, search across multiple documents
        if not request.document_id:
            # Search for relevant documents across all documents
            results = await chroma_engine.query_similar(
                query_text=request.query,
                n_results=request.max_results,  # This should now return multiple results
                filter_metadata={"document_type": "word"} if request.document_id is None else {"document_id": request.document_id}
            )
        else:
            # Specific document search
            results = await chroma_engine.query_similar(
                query_text=request.query,
                n_results=request.max_results,
                filter_metadata={"document_id": request.document_id}
            )

        # If no results found, provide general LLM response
        if not results["documents"] or all(not doc for doc in results["documents"]):
            prompt = f"""I couldn't find relevant information in the documents for: '{request.query}'
            Please provide a helpful response based on your general knowledge.
            
            Question: {request.query}
            
            Answer:"""
            
            answer = await llm_service.generate_text(prompt)
            
            response = QueryResponse(
                query=request.query,
                answer=answer,
                sources=[],
                relevance_scores=[],
                document_ids=[]
            )
        else:
            # Get context from multiple documents
            documents_context = []
            all_sources = []
            all_relevance_scores = []
            all_document_ids = []
            
            # Combine content from multiple documents with chunk indexing
            for i, doc_content in enumerate(results["documents"]):
                if doc_content.strip():  # Only add non-empty documents
                    # Extract chunk information if available in metadata
                    chunk_info = ""
                    if "metadatas" in results and i < len(results["metadatas"]):
                        metadata = results["metadatas"][i]
                        chunk_idx = metadata.get("chunk_index", "unknown")
                        doc_id = metadata.get("document_id", "unknown")
                        chunk_info = f"[Document: {doc_id}, Chunk: {chunk_idx}]"
                    
                    doc_context = f"{chunk_info}\n{doc_content}\n"
                    documents_context.append(doc_context)
                    all_sources.append(doc_content)
                    all_relevance_scores.append(float(1 - results["distances"][i]))
                    if "metadatas" in results and i < len(results["metadatas"]):
                        metadata = results["metadatas"][i]
                        if "document_id" in metadata:
                            all_document_ids.append(metadata["document_id"])
            
            # Join all document contexts
            combined_context = "\n\n".join(documents_context)
            
            # Create a more sophisticated prompt that uses multiple document sources
            prompt = f"""Based on the provided documents, answer the question. 
            Synthesize information from multiple sources when possible.

            Documents:
            {combined_context}

            Question: {request.query}

            Instructions:
            - Use information from multiple documents if relevant
            - Cite which document information comes from when possible
            - If information is in multiple documents, acknowledge this
            - Provide a comprehensive answer

            Answer:"""
            
            answer = await llm_service.generate_text(prompt)
            
            response = QueryResponse(
                query=request.query,
                answer=answer,
                sources=all_sources,
                relevance_scores=all_relevance_scores,
                document_ids=all_document_ids
            )

        # Cache result
        cache_manager.set(cache_key, response.dict())
        
        return response

    except Exception as e:
        logger.error(f"Error in ask question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))