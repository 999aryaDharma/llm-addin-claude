"""
Pydantic models for query operations
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ContextLayer(str, Enum):
    """Context layer types"""
    LOCAL = "local"
    SECTION = "section"
    GLOBAL = "global"


class QueryRequest(BaseModel):
    """Enhanced query request for Word"""
    query: str = Field(..., description="Search query text")
    document_id: Optional[str] = Field(None, description="Filter by document ID")
    max_results: int = Field(5, ge=1, le=20, description="Number of results")
    bypass_cache: bool = Field(False, description="Bypass cache")


class QueryResponse(BaseModel):
    """Enhanced query response"""
    query: str
    answer: str
    sources: List[str] = Field(default_factory=list)
    relevance_scores: List[float] = Field(default_factory=list)
    document_ids: List[str] = Field(default_factory=list)


class RewriteRequest(BaseModel):
    """Text rewrite request"""
    text: str = Field(..., description="Text to rewrite")
    instruction: str = Field(..., description="Rewriting instruction")
    style: Optional[str] = Field(None, description="Writing style (formal, casual, academic, persuasive, concise)")
    context: Optional[str] = Field(None, description="Additional context")
    use_context: bool = Field(False, description="Use document context from RAG")


class RewriteResponse(BaseModel):
    """Text rewrite response"""
    original: str
    rewritten: str
    changes: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeRequest(BaseModel):
    """Text analysis request"""
    text: str = Field(..., description="Text to analyze")
    analysis_type: str = Field("general", description="Type of analysis (general, style, grammar, readability, sentiment)")
    include_suggestions: bool = Field(True, description="Include improvement suggestions")


class AnalyzeResponse(BaseModel):
    """Text analysis response"""
    analysis: Any  # Can be string or dict
    metrics: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    """Document comparison request"""
    document_id_1: str = Field(..., description="First document ID")
    document_id_2: str = Field(..., description="Second document ID")
    comparison_type: str = Field("content", description="Type of comparison (content, style, structure)")


class CompareResponse(BaseModel):
    """Document comparison response"""
    comparison: str
    differences: List[Dict[str, Any]] = Field(default_factory=list)
    similarities: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SummarizeRequest(BaseModel):
    """Text summarization request"""
    text: str = Field(..., description="Text to summarize")
    summary_type: str = Field("concise", description="Type of summary (concise, detailed, bullets)")
    max_length: Optional[int] = Field(None, description="Maximum length in words")
    document_id: Optional[str] = Field(None, description="Document ID for context")


class SummarizeResponse(BaseModel):
    """Text summarization response"""
    summary: str
    key_points: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerateRequest(BaseModel):
    """Content generation request"""
    prompt: str = Field(..., description="Generation prompt")
    context: Optional[str] = Field(None, description="Additional context")
    style: str = Field("professional", description="Writing style")
    length: str = Field("medium", description="Desired length (short, medium, long)")
    document_id: Optional[str] = Field(None, description="Document ID for context")


class GenerateResponse(BaseModel):
    """Content generation response"""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextRequest(BaseModel):
    """Context layer request"""
    content: str = Field(..., description="Content to create context for")
    layer_type: str = Field("local", description="Context layer type (local, section, global)")
    document_id: Optional[str] = Field(None, description="Document ID")


class ContextResponse(BaseModel):
    """Context layer response"""
    layer_id: str
    content: str
    layer_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)