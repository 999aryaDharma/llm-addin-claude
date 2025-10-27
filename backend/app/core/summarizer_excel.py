"""
Excel data analysis and summarization module
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

from app.services.llm_service import llm_service
from app.config import settings

logger = logging.getLogger(__name__)


class ExcelSummarizer:
    """Analyze and summarize Excel data"""
    
    def __init__(self):
        self.llm = llm_service
    
    async def analyze_dataset(
        self,
        df: pd.DataFrame,
        include_statistics: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive dataset analysis
        
        Args:
            df: Pandas DataFrame
            include_statistics: Include statistical analysis
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                "shape": {"rows": len(df), "columns": len(df.columns)},
                "columns": [],
                "data_quality": {},
                "insights": []
            }
            
            # Analyze each column
            for col in df.columns:
                col_analysis = self._analyze_column(df[col])
                analysis["columns"].append(col_analysis)
            
            # Data quality assessment
            analysis["data_quality"] = self._assess_data_quality(df)
            
            # Generate AI insights if requested
            if include_statistics:
                insights = await self._generate_insights(df, analysis)
                analysis["insights"] = insights
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing dataset: {str(e)}")
            raise
    
    def _analyze_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze a single column"""
        col_info = {
            "name": series.name,
            "dtype": str(series.dtype),
            "non_null_count": int(series.count()),
            "null_count": int(series.isna().sum()),
            "unique_count": int(series.nunique())
        }
        
        # Type-specific analysis
        if pd.api.types.is_numeric_dtype(series):
            col_info["statistics"] = {
                "mean": float(series.mean()) if not series.empty else None,
                "median": float(series.median()) if not series.empty else None,
                "std": float(series.std()) if not series.empty else None,
                "min": float(series.min()) if not series.empty else None,
                "max": float(series.max()) if not series.empty else None
            }
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            # Get top values for categorical data
            value_counts = series.value_counts()
            col_info["top_values"] = value_counts.head(5).to_dict()
        
        return col_info
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isna().sum().sum()
        
        quality = {
            "completeness_score": float(((total_cells - null_cells) / total_cells * 100) if total_cells > 0 else 0),
            "total_missing": int(null_cells),
            "columns_with_missing": list(df.columns[df.isna().any()].tolist()),
            "duplicate_rows": int(df.duplicated().sum())
        }
        
        return quality
    
    async def _generate_insights(
        self,
        df: pd.DataFrame,
        basic_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate AI-powered insights from data"""
        try:
            # Create a summary for LLM
            summary = f"""Dataset Analysis:
- Rows: {basic_analysis['shape']['rows']}
- Columns: {basic_analysis['shape']['columns']}
- Data Quality Score: {basic_analysis['data_quality']['completeness_score']:.1f}%

Columns:
"""
            for col in basic_analysis['columns'][:10]:  # Limit to first 10 columns
                summary += f"\n- {col['name']} ({col['dtype']}): {col['non_null_count']} non-null values"
                if 'statistics' in col:
                    summary += f", mean: {col['statistics'].get('mean', 'N/A')}"
            
            prompt = f"""{summary}

Berdasarkan dataset ini, berikan 3-5 wawasan kunci atau rekomendasi untuk analisis.
Fokus pada masalah kualitas data, pola menarik, dan saran visualisasi."""

            response = await self.llm.generate_text(prompt)
            
            # Parse insights from response
            insights = [
                line.strip().lstrip('0123456789.-) ')
                for line in response.split('\n')
                if line.strip() and len(line.strip()) > 10
            ]
            
            return insights[:5]
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    async def find_correlations(
        self,
        df: pd.DataFrame,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Find significant correlations between numeric columns"""
        try:
            # Get numeric columns only
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.shape[1] < 2:
                return []
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Find significant correlations
            correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) >= threshold:
                        correlations.append({
                            "column1": corr_matrix.columns[i],
                            "column2": corr_matrix.columns[j],
                            "correlation": float(corr_value),
                            "strength": "strong" if abs(corr_value) > 0.7 else "moderate"
                        })
            
            # Sort by absolute correlation value
            correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error finding correlations: {str(e)}")
            return []
    
    async def recommend_chart(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Recommend appropriate chart type for data"""
        try:
            if columns:
                subset = df[columns]
            else:
                subset = df
            
            # Analyze data types
            numeric_cols = subset.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = subset.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Build context for LLM
            context = f"""Data characteristics:
- Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}
- Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}
- Row count: {len(subset)}
"""
            
            prompt = f"""{context}

Rekomendasikan jenis grafik terbaik untuk memvisualisasikan data ini.
Pertimbangkan: scatter plot, line chart, bar chart, pie chart, histogram, box plot, heatmap.

Berikan rekomendasi Anda beserta alasannya."""

            response = await self.llm.generate_json(
                prompt,
                schema={
                    "chart_type": "string",
                    "reasoning": "string",
                    "x_axis": "string",
                    "y_axis": "string",
                    "additional_config": "object"
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error recommending chart: {str(e)}")
            raise
    
    async def generate_pivot_suggestion(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Suggest pivot table configuration"""
        try:
            # Identify potential dimensions and measures
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if not categorical_cols or not numeric_cols:
                return {
                    "suitable": False,
                    "reason": "Need both categorical and numeric columns for pivot"
                }
            
            prompt = f"""Sarankan konfigurasi pivot table untuk data ini:

Kolom kategorikal (dimensi potensial): {', '.join(categorical_cols)}
Kolom numerik (ukuran potensial): {', '.join(numeric_cols)}

Berikan:
- Index (dimensi baris)
- Columns (dimensi kolom)
- Values (ukuran untuk diagregasi)
- Fungsi agregasi"""

            response = await self.llm.generate_json(
                prompt,
                schema={
                    "suitable": "boolean",
                    "index": "string",
                    "columns": "string",
                    "values": "string",
                    "aggfunc": "string",
                    "explanation": "string"
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating pivot suggestion: {str(e)}")
            raise


# Global instance
excel_summarizer = ExcelSummarizer()