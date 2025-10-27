"""
Pydantic models for document operations
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration"""
    WORD = "word"
    EXCEL = "excel"
    PDF = "pdf"
    TEXT = "text"


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentUpload(BaseModel):
    """Model for document upload request"""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")


class DocumentMetadata(BaseModel):
    """Document metadata"""
    document_id: str = Field(..., description="Unique document ID")
    filename: str
    document_type: DocumentType
    size: int
    upload_date: datetime = Field(default_factory=datetime.now)
    status: DocumentStatus = DocumentStatus.UPLOADING
    chunk_count: Optional[int] = None
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """Model for document chunks"""
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    success: bool
    document_id: Optional[str] = None
    message: str
    metadata: Optional[DocumentMetadata] = None


class DocumentListResponse(BaseModel):
    """Response for listing documents"""
    documents: List[DocumentMetadata]
    total: int
    page: int = 1
    page_size: int = 10


class DocumentSearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., description="Search query text")
    document_ids: Optional[List[str]] = Field(None, description="Filter by document IDs")
    document_types: Optional[List[DocumentType]] = Field(None, description="Filter by document types")
    limit: int = Field(5, ge=1, le=50, description="Number of results")
    include_metadata: bool = Field(True, description="Include metadata in results")


class DocumentSearchResult(BaseModel):
    """Single search result"""
    document_id: str
    chunk_id: str
    content: str
    score: float = Field(..., description="Similarity score")
    metadata: Optional[Dict[str, Any]] = None


class DocumentSearchResponse(BaseModel):
    """Search response model"""
    query: str
    results: List[DocumentSearchResult]
    total_found: int