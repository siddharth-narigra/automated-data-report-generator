"""
Data Analysis Module
Provides functions for dataset overview, data quality checks, and statistical summaries.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple


def get_dataset_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a comprehensive overview of the dataset.
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        Dictionary containing dataset shape, column info, and data types
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'numerical_columns': numerical_cols,
        'categorical_columns': categorical_cols,
        'numerical_count': len(numerical_cols),
        'categorical_count': len(categorical_cols),
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
    }


def get_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze data quality including missing values, duplicates, and constant columns.
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        Dictionary containing data quality metrics
    """
    # Missing values analysis
    missing_counts = df.isnull().sum()
    missing_percentages = (missing_counts / len(df) * 100).round(2)
    missing_data = {
        col: {'count': int(missing_counts[col]), 'percentage': float(missing_percentages[col])}
        for col in df.columns if missing_counts[col] > 0
    }
    
    # Duplicate rows
    duplicate_count = df.duplicated().sum()
    duplicate_percentage = round(duplicate_count / len(df) * 100, 2) if len(df) > 0 else 0
    
    # Constant columns (only one unique value)
    constant_columns = [col for col in df.columns if df[col].nunique() <= 1]
    
    # Near-constant columns (one value dominates 95%+)
    near_constant_columns = []
    for col in df.columns:
        if col not in constant_columns:
            value_counts = df[col].value_counts(normalize=True)
            if len(value_counts) > 0 and value_counts.iloc[0] >= 0.95:
                near_constant_columns.append({
                    'column': col,
                    'dominant_value': str(value_counts.index[0]),
                    'percentage': round(value_counts.iloc[0] * 100, 2)
                })
    
    return {
        'missing_values': missing_data,
        'total_missing_cells': int(missing_counts.sum()),
        'total_cells': len(df) * len(df.columns),
        'duplicate_rows': int(duplicate_count),
        'duplicate_percentage': duplicate_percentage,
        'constant_columns': constant_columns,
        'near_constant_columns': near_constant_columns
    }


def get_statistical_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate statistical summaries for numerical and categorical columns.
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        Dictionary containing statistical summaries
    """
    numerical_stats = {}
    categorical_stats = {}
    
    # Numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    for col in numerical_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            numerical_stats[col] = {
                'mean': round(col_data.mean(), 2),
                'median': round(col_data.median(), 2),
                'std': round(col_data.std(), 2),
                'min': round(col_data.min(), 2),
                'max': round(col_data.max(), 2),
                'q1': round(col_data.quantile(0.25), 2),
                'q3': round(col_data.quantile(0.75), 2)
            }
    
    # Categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        top_values = value_counts.head(5)
        categorical_stats[col] = {
            'unique_count': int(df[col].nunique()),
            'top_values': [
                {'value': str(val), 'count': int(count), 'percentage': round(count / len(df) * 100, 2)}
                for val, count in top_values.items()
            ]
        }
    
    return {
        'numerical': numerical_stats,
        'categorical': categorical_stats
    }


def get_correlation_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Calculate correlation matrix for numerical columns and identify strong correlations.
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        Tuple of (correlation matrix DataFrame, list of strong correlation pairs)
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numerical_cols) < 2:
        return pd.DataFrame(), []
    
    corr_matrix = df[numerical_cols].corr()
    
    # Find strong correlations (absolute value > 0.7)
    strong_correlations = []
    for i in range(len(numerical_cols)):
        for j in range(i + 1, len(numerical_cols)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > 0.7:
                strong_correlations.append({
                    'column_1': numerical_cols[i],
                    'column_2': numerical_cols[j],
                    'correlation': round(corr_value, 3)
                })
    
    return corr_matrix, strong_correlations
