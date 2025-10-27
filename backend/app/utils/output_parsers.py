"""
Output parsers for LangChain structured responses
"""
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import re


# Word Document Analysis Models
class WritingAnalysis(BaseModel):
    """Writing style analysis output"""
    tone: str = Field(description="Overall tone of the text")
    style: str = Field(description="Writing style (formal, casual, academic, etc)")
    readability_score: Optional[float] = Field(description="Readability score 0-100")
    suggestions: List[str] = Field(description="List of improvement suggestions")
    key_themes: List[str] = Field(description="Main themes identified")


class TextRewrite(BaseModel):
    """Text rewriting output"""
    original_text: str = Field(description="Original text")
    rewritten_text: str = Field(description="Rewritten version")
    changes: List[str] = Field(description="List of changes made")
    confidence: float = Field(description="Confidence score 0-1")


class Citation(BaseModel):
    """Citation information"""
    text: str = Field(description="Cited text")
    source: str = Field(description="Source of citation")
    page: Optional[int] = Field(description="Page number if available")
    confidence: float = Field(description="Confidence in citation accuracy")


# Excel Analysis Models
class FormulaGeneration(BaseModel):
    """Excel formula generation output"""
    formula: str = Field(description="Generated Excel formula")
    explanation: str = Field(description="Explanation of what the formula does")
    cell_range: Optional[str] = Field(description="Suggested cell range")
    example_result: Optional[str] = Field(description="Example calculation result")


class DataInsight(BaseModel):
    """Data analysis insight"""
    insight_type: str = Field(description="Type of insight (correlation, trend, outlier, etc)")
    description: str = Field(description="Description of the insight")
    affected_columns: List[str] = Field(description="Columns involved")
    confidence: float = Field(description="Confidence score 0-1")
    visualization_suggestion: Optional[str] = Field(description="Suggested chart type")


class ColumnAnalysis(BaseModel):
    """Analysis of a data column"""
    column_name: str
    data_type: str
    missing_values: int
    unique_values: int
    statistics: Optional[Dict[str, Any]] = Field(description="Statistical summary")
    insights: List[str] = Field(description="Key insights about this column")


class DatasetSummary(BaseModel):
    """Complete dataset summary"""
    row_count: int
    column_count: int
    columns: List[ColumnAnalysis]
    correlations: Optional[List[Dict[str, Any]]] = Field(description="Notable correlations")
    data_quality_score: float = Field(description="Overall data quality 0-100")
    recommendations: List[str] = Field(description="Recommendations for analysis")


class ChartRecommendation(BaseModel):
    """Chart type recommendation"""
    chart_type: str = Field(description="Recommended chart type")
    reasoning: str = Field(description="Why this chart type is suitable")
    x_axis: Optional[str] = Field(description="Suggested X-axis column")
    y_axis: Optional[str] = Field(description="Suggested Y-axis column")
    additional_series: Optional[List[str]] = Field(description="Additional data series")


# Comparison Models
class DocumentComparison(BaseModel):
    """Document comparison result"""
    similarity_score: float = Field(description="Similarity score 0-100")
    differences: List[str] = Field(description="Key differences")
    similarities: List[str] = Field(description="Key similarities")
    summary: str = Field(description="Overall comparison summary")


# Parser Factory
class OutputParserFactory:
    """Factory for creating output parsers"""
    
    @staticmethod
    def get_parser(model_class: type[BaseModel]) -> PydanticOutputParser:
        """Get Pydantic parser for a model class"""
        return PydanticOutputParser(pydantic_object=model_class)
    
    @staticmethod
    def get_json_parser() -> JsonOutputParser:
        """Get simple JSON parser"""
        return JsonOutputParser()
    
    @staticmethod
    def parse_markdown_json(text: str) -> Dict[str, Any]:
        """Parse JSON from markdown code blocks"""
        # Extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No JSON found in text")
        
        return json.loads(json_str)


# Convenience parsers
writing_analysis_parser = OutputParserFactory.get_parser(WritingAnalysis)
text_rewrite_parser = OutputParserFactory.get_parser(TextRewrite)
citation_parser = OutputParserFactory.get_parser(Citation)
formula_parser = OutputParserFactory.get_parser(FormulaGeneration)
data_insight_parser = OutputParserFactory.get_parser(DataInsight)
dataset_summary_parser = OutputParserFactory.get_parser(DatasetSummary)
chart_recommendation_parser = OutputParserFactory.get_parser(ChartRecommendation)
comparison_parser = OutputParserFactory.get_parser(DocumentComparison)