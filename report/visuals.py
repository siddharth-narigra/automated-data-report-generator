"""
Visualization Module
Generates charts and plots for data analysis, returning base64-encoded images.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from typing import List, Dict, Optional


def _fig_to_base64(fig: plt.Figure) -> str:
    """Convert matplotlib figure to base64 string."""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    return img_str


def generate_histograms(df: pd.DataFrame, max_cols: int = 6) -> List[Dict[str, str]]:
    """
    Generate histograms for numerical columns.
    
    Args:
        df: Input pandas DataFrame
        max_cols: Maximum number of columns to visualize
        
    Returns:
        List of dictionaries with column name and base64 image
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:max_cols]
    histograms = []
    
    for col in numerical_cols:
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue
            
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Style settings
        ax.hist(col_data, bins=30, color='#4F46E5', edgecolor='white', alpha=0.8)
        ax.set_xlabel(col, fontsize=11, fontweight='medium')
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'Distribution of {col}', fontsize=13, fontweight='bold', pad=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)
        
        histograms.append({
            'column': col,
            'image': _fig_to_base64(fig)
        })
    
    return histograms


def generate_bar_charts(df: pd.DataFrame, max_cols: int = 6) -> List[Dict[str, str]]:
    """
    Generate bar charts for categorical columns.
    
    Args:
        df: Input pandas DataFrame
        max_cols: Maximum number of columns to visualize
        
    Returns:
        List of dictionaries with column name and base64 image
    """
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()[:max_cols]
    bar_charts = []
    
    for col in categorical_cols:
        value_counts = df[col].value_counts().head(10)
        if len(value_counts) == 0:
            continue
            
        fig, ax = plt.subplots(figsize=(8, 5))
        
        colors = plt.cm.Purples(np.linspace(0.4, 0.8, len(value_counts)))
        bars = ax.barh(value_counts.index.astype(str), value_counts.values, color=colors, edgecolor='white')
        
        ax.set_xlabel('Count', fontsize=11)
        ax.set_ylabel(col, fontsize=11, fontweight='medium')
        ax.set_title(f'Top Values in {col}', fontsize=13, fontweight='bold', pad=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=0.3)
        
        # Add count labels
        for bar, count in zip(bars, value_counts.values):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                   str(count), va='center', fontsize=9)
        
        bar_charts.append({
            'column': col,
            'image': _fig_to_base64(fig)
        })
    
    return bar_charts


def generate_correlation_heatmap(df: pd.DataFrame) -> Optional[str]:
    """
    Generate a correlation heatmap for numerical columns.
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        Base64-encoded image string or None if insufficient numerical columns
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numerical_cols) < 2:
        return None
    
    # Limit to 15 columns for readability
    cols_to_use = numerical_cols[:15]
    corr_matrix = df[cols_to_use].corr()
    
    fig_size = max(8, min(12, len(cols_to_use) * 0.8))
    fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.8))
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    sns.heatmap(
        corr_matrix, 
        mask=mask,
        annot=True, 
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        cbar_kws={'shrink': 0.8},
        annot_kws={'size': 9}
    )
    
    ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    
    return _fig_to_base64(fig)


def generate_all_visuals(df: pd.DataFrame) -> Dict[str, any]:
    """
    Generate all visualizations for the dataset.
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        Dictionary containing all visual assets
    """
    return {
        'histograms': generate_histograms(df),
        'bar_charts': generate_bar_charts(df),
        'correlation_heatmap': generate_correlation_heatmap(df)
    }
