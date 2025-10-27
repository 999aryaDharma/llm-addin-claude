from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class DataType(str, Enum):
    """Excel data types"""
    NUMERIC = "numeric"
    STRING = "string"
    DATE = "date"
    BOOLEAN = "boolean"
    FORMULA = "formula"


class ExcelRange(BaseModel):
    """Excel range data"""
    sheet_name: str
    range_address: str
    data: List[List[Any]]  # Main data attribute
    values: Optional[List[List[Any]]] = None  # Alias for backward compatibility
    headers: Optional[List[str]] = None
    data_types: Optional[Dict[str, str]] = None

    def __init__(self, **data):
        # Handle both 'data' and 'values' parameters
        if 'values' in data and 'data' not in data:
            data['data'] = data['values']
        elif 'data' in data and 'values' not in data:
            data['values'] = data['data']
        super().__init__(**data)


class ExcelOperationResponse(BaseModel):
    """Response for Excel operations"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataQueryResponse(BaseModel):
    """Response model for natural language data queries"""
    answer: str
    relevant_data: Dict[str, Any] = Field(default_factory=dict)
    sql_equivalent: Optional[str] = None
    visualization_suggestion: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExcelQueryRequest(BaseModel):
    """Excel data query request"""
    query: str
    range_data: ExcelRange
    context: Optional[str] = None
    include_analysis: bool = True


class ExcelQueryResponse(BaseModel):
    """Excel data query response"""
    answer: str
    data: Optional[Dict[str, Any]] = None
    visualization_suggestion: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FormulaRequest(BaseModel):
    """Formula generation request"""
    description: str
    range_data: ExcelRange
    target_cell: Optional[str] = None
    context: Optional[str] = None


class FormulaResponse(BaseModel):
    """Formula generation response"""
    formula: str
    explanation: str
    example_result: Optional[Any] = None
    alternative_formulas: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InsightRequest(BaseModel):
    """Data insight request"""
    range_data: ExcelRange
    insight_type: str = "summary"  # summary, correlation, anomaly, trend
    context: Optional[str] = None


class InsightResponse(BaseModel):
    """Data insight response"""
    insights: List[str]
    statistics: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChartRequest(BaseModel):
    """Chart recommendation request"""
    range_data: ExcelRange
    purpose: Optional[str] = None
    context: Optional[str] = None


class ChartSuggestion(BaseModel):
    """Single chart suggestion"""
    chart_type: str
    title: str
    description: str
    config: Dict[str, Any]
    suitability_score: float


class ChartResponse(BaseModel):
    """Chart recommendation response"""
    suggestions: List[ChartSuggestion]
    best_choice: ChartSuggestion
    reasoning: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExcelAnalysisRequest(BaseModel):
    """Comprehensive Excel analysis request"""
    range_data: ExcelRange
    analysis_types: List[str] = Field(
        default=["summary", "statistics", "correlations", "anomalies"]
    )
    context: Optional[str] = None


class ExcelAnalysisResponse(BaseModel):
    """Comprehensive Excel analysis response"""
    summary: str
    statistics: Dict[str, Any] = Field(default_factory=dict)
    correlations: Optional[Dict[str, Any]] = None
    anomalies: Optional[List[Dict[str, Any]]] = None
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    chart_suggestions: Optional[List[ChartSuggestion]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PivotSuggestion(BaseModel):
    """Pivot table suggestion"""
    rows: List[str]
    columns: List[str]
    values: List[Dict[str, str]]
    filters: List[str] = Field(default_factory=list)
    suggested_name: Optional[str] = None


class CorrelationInfo(BaseModel):
    """Information about a correlation"""
    column1: str
    column2: str
    correlation_coefficient: float
    description: str


class DataQueryResponse(BaseModel):
    """Response model for natural language data queries"""
    answer: str
    relevant_data: Dict[str, Any] = Field(default_factory=dict)
    sql_equivalent: Optional[str] = None
    visualization_suggestion: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)