"""
Excel data parser and analyzer service
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

from app.models.excel import ExcelRange, DataType

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parse and analyze Excel data"""
    
    @staticmethod
    def range_to_dataframe(range_data: ExcelRange) -> pd.DataFrame:
        """
        Convert ExcelRange to pandas DataFrame
        
        Args:
            range_data: ExcelRange object with data and metadata
            
        Returns:
            pandas DataFrame
        """
        try:
            # Create DataFrame from data
            df = pd.DataFrame(range_data.data)
            
            # Set headers if provided
            if range_data.headers and len(range_data.headers) == len(df.columns):
                df.columns = range_data.headers
            elif len(range_data.data) > 0:
                # Use first row as headers
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
            
            # Infer data types
            for col in df.columns:
                try:
                    # Try to convert to numeric
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
            
            logger.info(f"Parsed range to DataFrame: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing range to DataFrame: {str(e)}")
            raise
    
    @staticmethod
    def detect_data_types(df: pd.DataFrame) -> Dict[str, DataType]:
        """
        Detect data types for each column
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dict mapping column names to DataType enum
        """
        type_map = {}
        
        for col in df.columns:
            dtype = df[col].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                type_map[col] = DataType.NUMERIC
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                type_map[col] = DataType.DATE
            elif pd.api.types.is_bool_dtype(dtype):
                type_map[col] = DataType.BOOLEAN
            else:
                # Check if it's a formula (contains '=')
                if df[col].dtype == 'object':
                    sample = df[col].dropna().astype(str).iloc[0] if len(df[col].dropna()) > 0 else ""
                    if sample.startswith('='):
                        type_map[col] = DataType.FORMULA
                    else:
                        type_map[col] = DataType.STRING
                else:
                    type_map[col] = DataType.STRING
        
        return type_map
    
    @staticmethod
    def get_statistics(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Get basic statistics for all columns
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dict with statistics for each column
        """
        stats = {}
        
        for col in df.columns:
            col_stats = {
                'count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'unique_count': int(df[col].nunique())
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    'mean': float(df[col].mean()) if not df[col].empty else None,
                    'median': float(df[col].median()) if not df[col].empty else None,
                    'std': float(df[col].std()) if not df[col].empty else None,
                    'min': float(df[col].min()) if not df[col].empty else None,
                    'max': float(df[col].max()) if not df[col].empty else None,
                    'q25': float(df[col].quantile(0.25)) if not df[col].empty else None,
                    'q75': float(df[col].quantile(0.75)) if not df[col].empty else None
                })
            elif df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
                # Get top values for categorical data
                value_counts = df[col].value_counts()
                col_stats['top_values'] = value_counts.head(5).to_dict()
            
            stats[str(col)] = col_stats
        
        return stats
    
    @staticmethod
    def analyze_column(series: pd.Series) -> Dict[str, Any]:
        """
        Analyze a single column
        
        Args:
            series: pandas Series
            
        Returns:
            Dict with column analysis
        """
        analysis = {
            'name': series.name,
            'dtype': str(series.dtype),
            'count': int(series.count()),
            'null_count': int(series.isnull().sum()),
            'unique_count': int(series.nunique())
        }
        
        if pd.api.types.is_numeric_dtype(series):
            analysis['statistics'] = {
                'mean': float(series.mean()) if not series.empty else None,
                'median': float(series.median()) if not series.empty else None,
                'std': float(series.std()) if not series.empty else None,
                'min': float(series.min()) if not series.empty else None,
                'max': float(series.max()) if not series.empty else None
            }
        elif series.dtype == 'object':
            value_counts = series.value_counts()
            analysis['top_values'] = value_counts.head(5).to_dict()
        
        return analysis
    
    @staticmethod
    def find_outliers(series: pd.Series, method: str = 'iqr') -> List[Any]:
        """
        Find outliers in a numeric series
        
        Args:
            series: pandas Series
            method: Method to use ('iqr' or 'zscore')
            
        Returns:
            List of outlier values
        """
        if not pd.api.types.is_numeric_dtype(series):
            return []
        
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            outliers = series[(series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)]
        else:  # zscore
            z_scores = np.abs((series - series.mean()) / series.std())
            outliers = series[z_scores > 3]
        
        return outliers.tolist()
    
    @staticmethod
    def suggest_chart_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Suggest appropriate chart types based on data
        
        Args:
            df: pandas DataFrame
            
        Returns:
            List of chart suggestions
        """
        suggestions = []
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # Time series detection
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                'type': 'line',
                'reason': 'Time series data detected',
                'x_axis': date_cols[0],
                'y_axis': numeric_cols[0]
            })
        
        # Categorical vs Numeric
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                'type': 'bar',
                'reason': 'Categorical and numeric data',
                'x_axis': categorical_cols[0],
                'y_axis': numeric_cols[0]
            })
        
        # Multiple numeric columns
        if len(numeric_cols) >= 2:
            suggestions.append({
                'type': 'scatter',
                'reason': 'Multiple numeric columns for correlation',
                'x_axis': numeric_cols[0],
                'y_axis': numeric_cols[1]
            })
        
        # Single categorical with counts
        if len(categorical_cols) == 1 and len(numeric_cols) == 0:
            suggestions.append({
                'type': 'pie',
                'reason': 'Single categorical variable',
                'column': categorical_cols[0]
            })
        
        # Distribution
        if len(numeric_cols) > 0:
            suggestions.append({
                'type': 'histogram',
                'reason': 'Show distribution of numeric data',
                'column': numeric_cols[0]
            })
        
        return suggestions
    
    @staticmethod
    def create_pivot_table(
        df: pd.DataFrame,
        index: str,
        columns: Optional[str] = None,
        values: str = None,
        aggfunc: str = 'mean'
    ) -> pd.DataFrame:
        """
        Create a pivot table from DataFrame
        
        Args:
            df: pandas DataFrame
            index: Column to use as index
            columns: Column to use as columns (optional)
            values: Column to aggregate
            aggfunc: Aggregation function
            
        Returns:
            Pivot table as DataFrame
        """
        try:
            if columns:
                pivot = pd.pivot_table(
                    df,
                    index=index,
                    columns=columns,
                    values=values,
                    aggfunc=aggfunc,
                    fill_value=0
                )
            else:
                pivot = df.groupby(index)[values].agg(aggfunc).reset_index()
            
            return pivot
        except Exception as e:
            logger.error(f"Error creating pivot table: {str(e)}")
            raise
    
    @staticmethod
    def validate_range(range_data: ExcelRange) -> Dict[str, Any]:
        """
        Validate range data
        
        Args:
            range_data: ExcelRange to validate
            
        Returns:
            Validation results
        """
        issues = []
        
        # Check if data is empty
        if not range_data.data or len(range_data.data) == 0:
            issues.append("Data is empty")
        
        # Check row count consistency
        if range_data.data:
            row_lengths = [len(row) for row in range_data.data]
            if len(set(row_lengths)) > 1:
                issues.append(f"Inconsistent row lengths: {set(row_lengths)}")
        
        # Check if headers match column count
        if range_data.headers and range_data.data:
            if len(range_data.headers) != len(range_data.data[0]):
                issues.append(f"Header count ({len(range_data.headers)}) doesn't match column count ({len(range_data.data[0])})")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


# Global instance
excel_parser = ExcelParser()