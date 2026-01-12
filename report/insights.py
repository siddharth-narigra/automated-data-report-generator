"""
Business Insights Module
Generates human-readable, actionable insights from data analysis results.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


def generate_missing_value_insights(quality_data: Dict[str, Any]) -> List[str]:
    """
    Generate insights about missing values in the dataset.
    
    Args:
        quality_data: Data quality analysis results
        
    Returns:
        List of human-readable insight strings
    """
    insights = []
    missing = quality_data.get('missing_values', {})
    
    if not missing:
        insights.append("✓ No missing values detected in any column - dataset is complete.")
        return insights
    
    # High missing value warnings (>20%)
    high_missing = [(col, data) for col, data in missing.items() if data['percentage'] > 20]
    for col, data in sorted(high_missing, key=lambda x: x[1]['percentage'], reverse=True):
        insights.append(
            f"⚠ Column '{col}' has {data['percentage']}% missing values ({data['count']:,} rows), "
            f"which may significantly impact analysis reliability."
        )
    
    # Moderate missing values (5-20%)
    moderate_missing = [(col, data) for col, data in missing.items() 
                        if 5 <= data['percentage'] <= 20]
    for col, data in moderate_missing:
        insights.append(
            f"Column '{col}' has {data['percentage']}% missing values - "
            f"consider imputation or exclusion strategy."
        )
    
    # Summary if many columns have issues
    if len(missing) > 3:
        total_missing = quality_data.get('total_missing_cells', 0)
        total_cells = quality_data.get('total_cells', 1)
        overall_pct = round(total_missing / total_cells * 100, 2)
        insights.append(
            f"Overall, {len(missing)} columns contain missing data, "
            f"representing {overall_pct}% of all data cells."
        )
    
    return insights


def generate_duplicate_insights(quality_data: Dict[str, Any]) -> List[str]:
    """
    Generate insights about duplicate rows.
    
    Args:
        quality_data: Data quality analysis results
        
    Returns:
        List of human-readable insight strings
    """
    insights = []
    dup_count = quality_data.get('duplicate_rows', 0)
    dup_pct = quality_data.get('duplicate_percentage', 0)
    
    if dup_count == 0:
        insights.append("✓ No duplicate rows detected - each record is unique.")
    elif dup_pct > 10:
        insights.append(
            f"⚠ Dataset contains {dup_count:,} duplicate rows ({dup_pct}%), "
            f"which may indicate data collection issues or require deduplication."
        )
    elif dup_count > 0:
        insights.append(
            f"Dataset contains {dup_count:,} duplicate rows ({dup_pct}%) - "
            f"review for potential data quality issues."
        )
    
    return insights


def generate_correlation_insights(strong_correlations: List[Dict[str, Any]]) -> List[str]:
    """
    Generate insights about correlations between variables.
    
    Args:
        strong_correlations: List of strong correlation pairs from analysis
        
    Returns:
        List of human-readable insight strings
    """
    insights = []
    
    if not strong_correlations:
        insights.append("No strong correlations (|r| > 0.7) detected between numerical variables.")
        return insights
    
    for corr in strong_correlations:
        col1 = corr['column_1']
        col2 = corr['column_2']
        r = corr['correlation']
        
        direction = "positive" if r > 0 else "negative"
        strength = "very strong" if abs(r) > 0.9 else "strong"
        
        insights.append(
            f"📊 {strength.capitalize()} {direction} correlation detected between "
            f"'{col1}' and '{col2}' (r = {r:.2f}). "
            f"These variables may be redundant or causally related."
        )
    
    if len(strong_correlations) > 3:
        insights.append(
            f"Multiple strong correlations detected ({len(strong_correlations)} pairs) - "
            f"consider feature selection or dimensionality reduction for modeling."
        )
    
    return insights


def generate_distribution_insights(stats: Dict[str, Any], df: pd.DataFrame) -> List[str]:
    """
    Generate insights about data distributions and categorical imbalances.
    
    Args:
        stats: Statistical summary results
        df: Original DataFrame for additional context
        
    Returns:
        List of human-readable insight strings
    """
    insights = []
    
    # Categorical distribution insights
    for col, col_stats in stats.get('categorical', {}).items():
        top_values = col_stats.get('top_values', [])
        if top_values:
            top_pct = top_values[0]['percentage']
            top_val = top_values[0]['value']
            
            if top_pct > 80:
                insights.append(
                    f"⚠ Column '{col}' is highly imbalanced - '{top_val}' represents {top_pct}% of values. "
                    f"This may affect model training if used as a target variable."
                )
            elif top_pct > 50:
                insights.append(
                    f"Category '{top_val}' dominates column '{col}' ({top_pct}%), "
                    f"indicating potential class imbalance."
                )
    
    # Numerical distribution insights
    for col, col_stats in stats.get('numerical', {}).items():
        mean = col_stats.get('mean', 0)
        median = col_stats.get('median', 0)
        std = col_stats.get('std', 0)
        
        # Check for skewness (mean vs median difference)
        if mean != 0 and abs(mean - median) / abs(mean) > 0.3:
            direction = "right-skewed" if mean > median else "left-skewed"
            insights.append(
                f"Column '{col}' appears {direction} (mean: {mean}, median: {median}). "
                f"Consider transformation for normality if required."
            )
        
        # Check for high variance
        if mean != 0 and std / abs(mean) > 1:
            insights.append(
                f"Column '{col}' has high variability (CV > 100%), "
                f"indicating diverse or potentially outlier-prone data."
            )
    
    return insights


def generate_size_insights(overview: Dict[str, Any]) -> List[str]:
    """
    Generate insights about dataset size and structure.
    
    Args:
        overview: Dataset overview results
        
    Returns:
        List of human-readable insight strings
    """
    insights = []
    rows = overview.get('rows', 0)
    cols = overview.get('columns', 0)
    num_cols = overview.get('numerical_count', 0)
    cat_cols = overview.get('categorical_count', 0)
    
    # Dataset size context
    if rows < 100:
        insights.append(
            f"⚠ Small dataset ({rows:,} rows) - statistical conclusions may have limited reliability."
        )
    elif rows > 100000:
        insights.append(
            f"Large dataset ({rows:,} rows) - consider sampling for initial exploration "
            f"or use scalable processing methods."
        )
    else:
        insights.append(
            f"Dataset contains {rows:,} rows and {cols} columns, "
            f"suitable for standard analysis approaches."
        )
    
    # Column composition
    insights.append(
        f"Column composition: {num_cols} numerical and {cat_cols} categorical features."
    )
    
    return insights


def generate_all_insights(
    overview: Dict[str, Any],
    quality: Dict[str, Any],
    stats: Dict[str, Any],
    correlations: List[Dict[str, Any]],
    df: pd.DataFrame
) -> List[str]:
    """
    Aggregate all insights into a comprehensive list.
    
    Args:
        overview: Dataset overview results
        quality: Data quality analysis results
        stats: Statistical summary results
        correlations: Strong correlation pairs
        df: Original DataFrame
        
    Returns:
        Complete list of all generated insights
    """
    all_insights = []
    
    # Size and structure
    all_insights.extend(generate_size_insights(overview))
    
    # Data quality
    all_insights.extend(generate_missing_value_insights(quality))
    all_insights.extend(generate_duplicate_insights(quality))
    
    # Distributions
    all_insights.extend(generate_distribution_insights(stats, df))
    
    # Correlations
    all_insights.extend(generate_correlation_insights(correlations))
    
    return all_insights
