"""
Excel data query endpoints - natural language queries for spreadsheet data
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
import pandas as pd
import logging

from app.models.excel import (
    ExcelQueryRequest,
    ExcelQueryResponse,
    FormulaRequest,
    FormulaResponse,
    InsightRequest,
    InsightResponse,
    ExcelRange,
    ChartSuggestion,
    PivotSuggestion,
    CorrelationInfo,
    DataQueryResponse
)
from app.services.excel_parser import excel_parser
from app.core.summarizer_excel import excel_summarizer
from app.services.llm_service import llm_service
from app.core.cache_manager import cache_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=ExcelQueryResponse)
async def query_data(request: ExcelQueryRequest):
    """
    Natural language query for Excel data
    
    Example queries:
    - "What is the average sales by region?"
    - "Which product has the highest revenue?"
    - "Show me the top 5 customers by order count"
    """
    try:
        # Parse range data to DataFrame
        df = excel_parser.range_to_dataframe(request.context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Get basic statistics
        stats = excel_parser.get_statistics(df)
        
        # Build context for LLM
        context_str = f"""Dataset Information:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Column names: {', '.join(df.columns)}

Column Statistics:
"""
        for col, col_stats in stats.items():
            context_str += f"\n{col}: {col_stats}"
        
        # Sample data
        sample_data = df.head(5).to_dict('records')
        context_str += f"\n\nSample data (first 5 rows):\n{sample_data}"
        
        # Query with LLM
        prompt = f"""{context_str}

User Query: {request.query}

Analyze the data and provide:
1. A direct answer to the query
2. Relevant data/numbers to support the answer
3. SQL-like query that would answer this (conceptual)
4. Visualization suggestion if applicable

Return as JSON with keys: answer, relevant_data, sql_equivalent, visualization_suggestion"""
        
        result = await llm_service.generate_json(prompt)
        
        # Extract relevant data from DataFrame
        relevant_data = {}
        try:
            # Try to extract actual data based on query
            query_lower = request.query.lower()
            
            if 'average' in query_lower or 'mean' in query_lower:
                for col in df.select_dtypes(include=['number']).columns:
                    relevant_data[f"avg_{col}"] = float(df[col].mean())
                    
            elif 'sum' in query_lower or 'total' in query_lower:
                for col in df.select_dtypes(include=['number']).columns:
                    relevant_data[f"sum_{col}"] = float(df[col].sum())
                    
            elif 'max' in query_lower or 'highest' in query_lower:
                for col in df.select_dtypes(include=['number']).columns:
                    max_val = df[col].max()
                    relevant_data[f"max_{col}"] = float(max_val)
                    
            elif 'min' in query_lower or 'lowest' in query_lower:
                for col in df.select_dtypes(include=['number']).columns:
                    min_val = df[col].min()
                    relevant_data[f"min_{col}"] = float(min_val)
        except Exception as e:
            logger.warning(f"Error extracting relevant data: {e}")
        
        return DataQueryResponse(
            answer=result.get("answer", "Unable to generate answer"),
            relevant_data=result.get("relevant_data", relevant_data),
            sql_equivalent=result.get("sql_equivalent"),
            visualization_suggestion=result.get("visualization_suggestion")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in query_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/formula", response_model=FormulaResponse)
async def generate_formula(request: FormulaRequest):
    """
    Generate Excel formula from natural language description
    
    Examples:
    - "Sum of column A"
    - "Average of B2:B10 if column C is greater than 100"
    - "Count unique values in column D"
    """
    try:
        # Build context if range provided
        context_str = ""
        if request.context:
            df = excel_parser.range_to_dataframe(request.context)
            context_str = f"""
Available columns: {', '.join(df.columns)}
Range: {request.context.range_address}
Sheet: {request.context.sheet_name or 'Active sheet'}
"""
        
        # Generate formula
        prompt = f"""Generate an Excel formula based on this description:

Description: {request.description}

{context_str}

{f"Target cell: {request.target_cell}" if request.target_cell else ""}

Provide:
1. The Excel formula
2. Explanation of how it works
3. Example result
4. Cell references used

Return as JSON with keys: formula, explanation, example_result, cell_references (array)"""
        
        result = await llm_service.generate_json(prompt)
        
        return FormulaResponse(
            formula=result.get("formula", "=ERROR()"),
            explanation=result.get("explanation", "Unable to generate formula"),
            example_result=result.get("example_result"),
            cell_references=result.get("cell_references", [])
        )
        
    except Exception as e:
        logger.error(f"Error in generate_formula: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-formula")
async def explain_formula(formula: str, context: Optional[ExcelRange] = None):
    """
    Explain an existing Excel formula
    
    Args:
        formula: Excel formula to explain (e.g., "=SUMIF(A:A,">100",B:B)")
        context: Optional range data for context
    """
    try:
        context_str = ""
        if context:
            df = excel_parser.range_to_dataframe(context)
            context_str = f"Context: Columns {', '.join(df.columns)}"
        
        prompt = f"""Explain this Excel formula in simple terms:

Formula: {formula}
{context_str}

Provide:
1. What the formula does
2. Breakdown of each function/operator
3. Example of when to use it
4. Common mistakes to avoid

Return as JSON with keys: explanation, breakdown, use_cases, common_mistakes"""
        
        result = await llm_service.generate_json(prompt)
        
        return {
            "success": True,
            "formula": formula,
            "explanation": result
        }
        
    except Exception as e:
        logger.error(f"Error explaining formula: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insight", response_model=InsightResponse)
async def get_insights(request: InsightRequest):
    """
    Get comprehensive insights from Excel data
    
    Includes:
    - Data analysis
    - Correlations
    - Recommendations
    - Chart suggestions
    """
    try:
        # Check cache
        cache_key = f"insight_{hash(str(request.context.data))}"
        cached = cache_manager.get(cache_key)
        if cached:
            return InsightResponse(**cached)
        
        # Parse to DataFrame
        df = excel_parser.range_to_dataframe(request.context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Comprehensive analysis
        analysis = await excel_summarizer.analyze_dataset(
            df,
            include_statistics=True
        )
        
        # Find correlations if requested
        correlations = []
        if request.find_correlations:
            corr_results = await excel_summarizer.find_correlations(df, threshold=0.5)
            correlations = [
                CorrelationInfo(**corr) for corr in corr_results
            ]
        
        # Get chart suggestions
        chart_result = await excel_summarizer.recommend_chart(df)
        chart_suggestions = [chart_result] if chart_result else []
        
        # Generate recommendations
        prompt = f"""Based on this data analysis, provide actionable recommendations:

Data Shape: {analysis['shape']['rows']} rows × {analysis['shape']['columns']} columns
Data Quality Score: {analysis['data_quality']['completeness_score']}%

Key Insights: {analysis.get('insights', [])}

Provide 5 specific recommendations for:
1. Data quality improvements
2. Further analysis to perform
3. Visualizations to create
4. Business actions to take

Return as JSON array of strings."""
        
        recommendations_result = await llm_service.generate_json(prompt)
        recommendations = recommendations_result if isinstance(recommendations_result, list) else []
        
        response_data = {
            "analysis": analysis,
            "correlations": correlations,
            "recommendations": recommendations,
            "chart_suggestions": chart_suggestions
        }
        
        # Cache result
        cache_manager.set(cache_key, response_data, ttl=1800)
        
        return InsightResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chart-recommend")
async def recommend_chart(context: ExcelRange, columns: Optional[List[str]] = None):
    """
    Recommend best chart type for data
    
    Args:
        context: Range data
        columns: Specific columns to visualize (optional)
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Filter columns if specified
        if columns:
            df = df[columns]
        
        # Get recommendation
        recommendation = await excel_summarizer.recommend_chart(df, columns)
        
        return {
            "success": True,
            "recommendation": ChartSuggestion(**recommendation)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recommending chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pivot-suggest")
async def suggest_pivot(context: ExcelRange):
    """
    Suggest pivot table configuration
    
    Args:
        context: Range data
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        suggestion = await excel_summarizer.generate_pivot_suggestion(df)
        
        return {
            "success": True,
            "suggestion": PivotSuggestion(**suggestion)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting pivot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-patterns")
async def find_patterns(context: ExcelRange):
    """
    Find patterns and anomalies in data
    
    Args:
        context: Range data
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Get statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        patterns = []
        
        for col in numeric_cols:
            # Check for outliers using IQR
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            
            if len(outliers) > 0:
                patterns.append({
                    "type": "outliers",
                    "column": col,
                    "count": len(outliers),
                    "description": f"Found {len(outliers)} outliers in {col}"
                })
            
            # Check for trends
            if len(df) > 3:
                trend = "increasing" if df[col].is_monotonic_increasing else \
                        "decreasing" if df[col].is_monotonic_decreasing else "mixed"
                if trend != "mixed":
                    patterns.append({
                        "type": "trend",
                        "column": col,
                        "trend": trend,
                        "description": f"{col} shows {trend} trend"
                    })
        
        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            patterns.append({
                "type": "duplicates",
                "count": int(dup_count),
                "description": f"Found {dup_count} duplicate rows"
            })
        
        # Use LLM for deeper pattern analysis
        prompt = f"""Analyze this dataset for patterns:

Shape: {df.shape}
Columns: {list(df.columns)}
Sample: {df.head(3).to_dict('records')}

Identified patterns: {patterns}

Find additional patterns like:
- Seasonal trends
- Correlations
- Groupings
- Unusual distributions

Return as JSON array of pattern objects."""
        
        llm_patterns = await llm_service.generate_json(prompt)
        if isinstance(llm_patterns, list):
            patterns.extend(llm_patterns)
        
        return {
            "success": True,
            "patterns": patterns,
            "metadata": {
                "rows": len(df),
                "columns": len(df.columns),
                "patterns_found": len(patterns)
            }
        }
        
    except Exception as e:
        logger.error(f"Error finding patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-quality")
async def check_data_quality(context: ExcelRange):
    """
    Comprehensive data quality check
    
    Args:
        context: Range data
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Quality metrics
        total_cells = df.shape[0] * df.shape[1]
        null_count = df.isnull().sum().sum()
        
        quality_report = {
            "completeness": {
                "score": ((total_cells - null_count) / total_cells * 100) if total_cells > 0 else 0,
                "total_cells": int(total_cells),
                "null_cells": int(null_count),
                "complete_cells": int(total_cells - null_count)
            },
            "consistency": {
                "duplicate_rows": int(df.duplicated().sum()),
                "columns_with_nulls": df.columns[df.isnull().any()].tolist()
            },
            "validity": {},
            "recommendations": []
        }
        
        # Check data types
        for col in df.columns:
            # Check if numeric column has non-numeric values
            if df[col].dtype == 'object':
                try:
                    pd.to_numeric(df[col], errors='raise')
                except:
                    quality_report["validity"][col] = "Contains non-numeric values"
        
        # Generate recommendations
        if null_count > 0:
            quality_report["recommendations"].append(
                f"Address {null_count} missing values ({null_count/total_cells*100:.1f}% of data)"
            )
        
        if df.duplicated().sum() > 0:
            quality_report["recommendations"].append(
                f"Remove or investigate {df.duplicated().sum()} duplicate rows"
            )
        
        return {
            "success": True,
            "quality_report": quality_report,
            "overall_score": quality_report["completeness"]["score"]
        }
        
    except Exception as e:
        logger.error(f"Error checking data quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))