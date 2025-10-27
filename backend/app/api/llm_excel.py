"""
LLM operations specifically for Excel data
Advanced analysis, transformations, and AI-powered insights
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
import logging

from app.models.excel import (
    ExcelRange,
    ExcelOperationResponse
)
from app.models.response import BaseResponse
from app.services.excel_parser import excel_parser
from app.core.summarizer_excel import excel_summarizer
from app.services.llm_service import llm_service
from app.core.cache_manager import cache_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze-comprehensive")
async def comprehensive_analysis(
    context: ExcelRange,
    include_correlations: bool = True,
    include_predictions: bool = False
):
    """
    Comprehensive AI-powered data analysis
    
    Includes:
    - Statistical analysis
    - Pattern detection
    - Correlations
    - Trends
    - Anomalies
    - Predictions (optional)
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Basic analysis
        analysis = await excel_summarizer.analyze_dataset(df, include_statistics=True)
        
        # Correlations
        correlations = []
        if include_correlations:
            corr_results = await excel_summarizer.find_correlations(df, threshold=0.3)
            correlations = corr_results
        
        # Find patterns and anomalies
        patterns = []
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            # Outlier detection
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            
            if len(outliers) > 0:
                patterns.append({
                    "type": "outliers",
                    "column": col,
                    "count": len(outliers),
                    "values": outliers[col].tolist()[:5]  # First 5 outliers
                })
            
            # Trend detection
            if len(df) > 5:
                # Simple trend using linear regression
                x = np.arange(len(df))
                y = df[col].values
                z = np.polyfit(x, y, 1)
                slope = z[0]
                
                if abs(slope) > 0.1 * df[col].std():
                    patterns.append({
                        "type": "trend",
                        "column": col,
                        "direction": "increasing" if slope > 0 else "decreasing",
                        "strength": float(abs(slope))
                    })
        
        # LLM-powered insights
        summary_text = f"""Dataset Analysis:
- Shape: {df.shape[0]} rows × {df.shape[1]} columns
- Columns: {list(df.columns)}
- Data Quality: {analysis['data_quality']['completeness_score']}%
- Patterns Found: {len(patterns)}
- Correlations: {len(correlations)}

Key Statistics:
{analysis['columns'][:3]}

Patterns: {patterns}
"""
        
        prompt = f"""{summary_text}

Berikan wawasan bisnis komprehensif termasuk:
1. Temuan kunci (3-5 yang paling penting)
2. Implikasi bisnis
3. Tindakan yang direkomendasikan
4. Area yang menjadi perhatian
5. Peluang yang teridentifikasi

Kembalikan dalam format JSON dengan keys: key_findings, implications, recommendations, concerns, opportunities"""
        
        insights = await llm_service.generate_json(prompt)
        
        # Predictions (if requested)
        predictions = None
        if include_predictions and len(numeric_cols) > 0:
            pred_col = numeric_cols[0]
            prompt_pred = f"""Berdasarkan data untuk kolom '{pred_col}':
Nilai terbaru: {df[pred_col].tail(10).tolist()}

Prediksi 3 nilai berikutnya dan berikan:
1. Nilai yang diprediksi
2. Tingkat kepercayaan (0-100)
3. Alasan

Kembalikan dalam format JSON."""
            
            predictions = await llm_service.generate_json(prompt_pred)
        
        return ExcelOperationResponse(
            success=True,
            message="Comprehensive analysis completed",
            data={
                "analysis": analysis,
                "correlations": correlations,
                "patterns": patterns,
                "insights": insights,
                "predictions": predictions
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report")
async def generate_report(
    context: ExcelRange,
    report_type: str = "executive",
    include_charts: bool = True
):
    """
    Generate AI-powered report from data
    
    Report types:
    - executive: High-level summary for executives
    - detailed: In-depth analysis
    - technical: Statistical and technical details
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Get comprehensive analysis
        analysis = await excel_summarizer.analyze_dataset(df, include_statistics=True)
        
        # Report prompts by type
        report_prompts = {
            "executive": """Buatlah laporan ringkasan eksekutif:
- Metrik kunci (3-5 angka terpenting)
- Temuan utama dalam poin-poin
- Rekomendasi strategis (3 teratas)
- Area risiko yang memerlukan perhatian
Buatlah ringkas dan fokus pada bisnis.""",

            "detailed": """Buatlah laporan analitis terperinci:
- Tinjauan data dan penilaian kualitas
- Temuan analisis statistik
- Analisis tren
- Wawasan korelasi
- Hasil deteksi pola
- Rekomendasi terperinci dengan alasan
Sertakan detail teknis tetapi tetap mudah diakses.""",

            "technical": """Buatlah laporan analisis teknis:
- Ringkasan statistik (mean, median, std dev)
- Analisis distribusi
- Hasil uji hipotesis
- Analisis regresi jika berlaku
- Rekomendasi teknis
- Catatan metodologi
Fokus pada ketelitian statistik dan akurasi teknis."""
        }
        
        prompt = f"""{report_prompts.get(report_type, report_prompts['executive'])}

Data Context:
- Dataset: {df.shape[0]} rows × {df.shape[1]} columns
- Columns: {list(df.columns)}
- Quality Score: {analysis['data_quality']['completeness_score']}%

Ringkasan Analisis:
{analysis}

Buatlah laporan dalam format markdown."""
        
        report = await llm_service.generate_text(prompt)
        
        # Chart suggestions if requested
        chart_suggestions = []
        if include_charts:
            chart_rec = await excel_summarizer.recommend_chart(df)
            if chart_rec:
                chart_suggestions.append(chart_rec)
        
        return ExcelOperationResponse(
            success=True,
            message=f"{report_type.capitalize()} report generated",
            data={
                "report": report,
                "report_type": report_type,
                "chart_suggestions": chart_suggestions,
                "generated_at": pd.Timestamp.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-transformations")
async def suggest_transformations(context: ExcelRange):
    """
    Suggest data transformations to improve analysis
    
    Suggests:
    - Data cleaning steps
    - Column transformations
    - Aggregations
    - Derived columns
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Analyze data quality issues
        issues = []
        suggestions = []
        
        # Check for nulls
        null_cols = df.columns[df.isnull().any()].tolist()
        if null_cols:
            issues.append(f"Missing values in: {', '.join(null_cols)}")
            suggestions.append({
                "type": "data_cleaning",
                "action": "fill_nulls",
                "columns": null_cols,
                "description": "Fill or remove missing values",
                "methods": ["forward fill", "mean/median", "remove rows"]
            })
        
        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            issues.append(f"{dup_count} duplicate rows")
            suggestions.append({
                "type": "data_cleaning",
                "action": "remove_duplicates",
                "description": "Remove duplicate rows",
                "impact": f"Will reduce dataset by {dup_count} rows"
            })
        
        # Suggest normalization for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            suggestions.append({
                "type": "transformation",
                "action": "normalize",
                "columns": numeric_cols.tolist(),
                "description": "Normalize numeric columns for better comparison",
                "methods": ["min-max scaling", "z-score standardization"]
            })
        
        # Suggest aggregations
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                "type": "aggregation",
                "action": "group_by",
                "group_columns": categorical_cols.tolist()[:2],
                "aggregate_columns": numeric_cols.tolist()[:2],
                "description": "Create summary statistics by categories"
            })
        
        # LLM suggestions
        data_summary = f"""Data shape: {df.shape}
Columns: {list(df.columns)}
Data types: {df.dtypes.to_dict()}
Issues found: {issues}

Sample data:
{df.head(3).to_dict('records')}"""
        
        prompt = f"""{data_summary}

Sarankan transformasi data tambahan yang akan:
1. Meningkatkan kualitas data
2. Mengungkap wawasan tersembunyi
3. Mempersiapkan data untuk analisis
4. Membuat kolom turunan yang berguna

Kembalikan sebagai array JSON dari saran transformasi."""
        
        llm_suggestions = await llm_service.generate_json(prompt)
        if isinstance(llm_suggestions, list):
            suggestions.extend(llm_suggestions)
        
        return ExcelOperationResponse(
            success=True,
            message="Transformation suggestions generated",
            data={
                "issues": issues,
                "suggestions": suggestions,
                "data_shape": df.shape,
                "columns": list(df.columns)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting transformations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-trends")
async def predict_trends(
    context: ExcelRange,
    target_column: str,
    periods: int = 5
):
    """
    Predict future trends for a column
    
    Args:
        context: Range data
        target_column: Column to predict
        periods: Number of future periods to predict
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        if target_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{target_column}' not found")
        
        # Get historical data
        historical = df[target_column].dropna()
        
        if len(historical) < 3:
            raise HTTPException(status_code=400, detail="Need at least 3 data points")
        
        # Simple trend prediction using polynomial fit
        x = np.arange(len(historical))
        y = historical.values
        
        # Fit polynomial (degree 2 for simple trend)
        z = np.polyfit(x, y, 2)
        p = np.poly1d(z)
        
        # Predict future values
        future_x = np.arange(len(historical), len(historical) + periods)
        predictions = [float(p(i)) for i in future_x]
        
        # Calculate confidence (simplified)
        residuals = y - p(x)
        std_error = np.std(residuals)
        confidence = max(0, min(100, 100 - (std_error / np.mean(y) * 100)))
        
        # LLM interpretation
        prompt = f"""Analisis prediksi tren ini:

Kolom: {target_column}
Nilai historis: {historical.tail(10).tolist()}
Nilai yang diprediksi: {predictions}
Kepercayaan prediksi: {confidence:.1f}%

Berikan:
1. Interpretasi tren
2. Penilaian kepercayaan
3. Faktor yang mungkin mempengaruhi akurasi
4. Implikasi bisnis
5. Rekomendasi

Kembalikan dalam format JSON."""
        
        interpretation = await llm_service.generate_json(prompt)
        
        return ExcelOperationResponse(
            success=True,
            message="Trend prediction completed",
            data={
                "target_column": target_column,
                "historical_count": len(historical),
                "predictions": predictions,
                "confidence": float(confidence),
                "interpretation": interpretation,
                "method": "polynomial_regression"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-datasets")
async def compare_datasets(
    dataset1: ExcelRange,
    dataset2: ExcelRange,
    comparison_type: str = "comprehensive"
):
    """
    Compare two Excel datasets
    
    Comparison types:
    - comprehensive: Full comparison
    - structure: Compare structure only
    - values: Compare values only
    - statistics: Compare statistics
    """
    try:
        df1 = excel_parser.range_to_dataframe(dataset1)
        df2 = excel_parser.range_to_dataframe(dataset2)
        
        if df1.empty or df2.empty:
            raise HTTPException(status_code=400, detail="One or both datasets are empty")
        
        comparison = {
            "structure": {
                "shape_match": df1.shape == df2.shape,
                "dataset1_shape": df1.shape,
                "dataset2_shape": df2.shape,
                "common_columns": list(set(df1.columns) & set(df2.columns)),
                "unique_to_dataset1": list(set(df1.columns) - set(df2.columns)),
                "unique_to_dataset2": list(set(df2.columns) - set(df1.columns))
            }
        }
        
        # Compare statistics for common columns
        common_cols = comparison["structure"]["common_columns"]
        if common_cols:
            stats_comparison = {}
            for col in common_cols:
                if pd.api.types.is_numeric_dtype(df1[col]) and pd.api.types.is_numeric_dtype(df2[col]):
                    stats_comparison[col] = {
                        "dataset1_mean": float(df1[col].mean()),
                        "dataset2_mean": float(df2[col].mean()),
                        "difference": float(df2[col].mean() - df1[col].mean()),
                        "percent_change": float((df2[col].mean() - df1[col].mean()) / df1[col].mean() * 100)
                                          if df1[col].mean() != 0 else None
                    }
            
            comparison["statistics"] = stats_comparison
        
        # LLM analysis
        prompt = f"""Bandingkan kedua dataset ini:

Dataset 1:
- Bentuk: {df1.shape}
- Kolom: {list(df1.columns)}

Dataset 2:
- Bentuk: {df2.shape}
- Kolom: {list(df2.columns)}

Perbandingan struktural: {comparison['structure']}
Perbandingan statistik: {comparison.get('statistics', {})}

Berikan:
1. Perbedaan kunci
2. Kesamaan kunci
3. Perbandingan kualitas data
4. Rekomendasi untuk rekonsiliasi
5. Masalah potensial

Kembalikan dalam format JSON."""
        
        analysis = await llm_service.generate_json(prompt)
        
        return ExcelOperationResponse(
            success=True,
            message="Dataset comparison completed",
            data={
                "comparison": comparison,
                "analysis": analysis
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-data")
async def explain_data(context: ExcelRange, focus: Optional[str] = None):
    """
    Get natural language explanation of data
    
    Args:
        context: Range data
        focus: Optional focus area (summary, patterns, quality, business)
    """
    try:
        df = excel_parser.range_to_dataframe(context)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data in range")
        
        # Get basic info
        analysis = await excel_summarizer.analyze_dataset(df)
        
        # Build context
        context_text = f"""Dataset Overview:
- Rows: {df.shape[0]}, Columns: {df.shape[1]}
- Column names: {list(df.columns)}
- Data quality: {analysis['data_quality']['completeness_score']}%
- Missing values: {analysis['data_quality']['total_missing']}

Sample data (first 3 rows):
{df.head(3).to_dict('records')}

Statistics:
{analysis['columns'][:5]}
"""
        
        focus_prompts = {
            "summary": "Berikan ringkasan singkat tentang apa yang diwakili data ini dan karakteristik kuncinya.",
            "patterns": "Jelaskan pola, tren, atau anomali apa pun yang terlihat dalam data ini.",
            "quality": "Nilai dan jelaskan kualitas data, kelengkapan, dan masalah apa pun.",
            "business": "Jelaskan data ini dari perspektif bisnis - wawasan apa yang dapat diperoleh dan tindakan apa yang direkomendasikan."
        }

        prompt = f"""{context_text}

{focus_prompts.get(focus, focus_prompts['summary'])}

Jelaskan dalam bahasa yang jelas dan non-teknis yang dapat dipahami pengguna bisnis."""
        
        explanation = await llm_service.generate_text(prompt)
        
        return ExcelOperationResponse(
            success=True,
            message="Data explanation generated",
            data={
                "explanation": explanation,
                "focus": focus or "summary",
                "data_shape": df.shape,
                "quality_score": analysis['data_quality']['completeness_score']
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))