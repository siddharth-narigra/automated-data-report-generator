"""
Automated Data Report Generator
A Streamlit app that converts raw CSV files into business-ready reports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Import report modules
from report.analysis import (
    get_dataset_overview,
    get_data_quality,
    get_statistical_summary,
    get_correlation_matrix
)
from report.visuals import generate_all_visuals
from report.insights import generate_all_insights


# Page configuration
st.set_page_config(
    page_title="Data Report Generator",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #4F46E5, #6366F1);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .section-divider {
        border-top: 2px solid #E5E7EB;
        margin: 2rem 0;
    }
    .insight-card {
        background: #F9FAFB;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4F46E5;
        margin-bottom: 0.75rem;
    }
    .insight-warning {
        border-left-color: #F59E0B;
    }
    .insight-success {
        border-left-color: #10B981;
    }
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5, #6366F1);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338CA, #4F46E5);
    }
</style>
""", unsafe_allow_html=True)


def number_format(value):
    """Format number with thousand separators."""
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return str(value)


def generate_html_report(overview, quality, stats, visuals, insights):
    """Generate HTML report using Jinja2 template."""
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['number_format'] = number_format
    
    template = env.get_template("report.html")
    
    html_content = template.render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        overview=overview,
        quality=quality,
        stats=stats,
        visuals=visuals,
        insights=insights
    )
    
    return html_content


def main():
    """Main application function."""
    
    # Header
    st.markdown('<p class="main-header">📊 Automated Data Report Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload a CSV file and instantly generate a comprehensive, business-ready data report.</p>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### 📁 Upload Your Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload any CSV file to generate an automated analysis report"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            df = pd.read_csv(uploaded_file)
            
            if df.empty:
                st.error("❌ The uploaded CSV file is empty. Please upload a file with data.")
                return
            
            # Display file info
            st.success(f"✅ Successfully loaded: **{uploaded_file.name}**")
            
            # Quick metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Numerical", len(df.select_dtypes(include=['number']).columns))
            with col4:
                st.metric("Categorical", len(df.select_dtypes(include=['object', 'category']).columns))
            
            # Data preview
            with st.expander("📋 Preview Data (First 10 Rows)", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Column info
            with st.expander("📝 Column Information"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null Count': df.count().values,
                    'Null Count': df.isnull().sum().values
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            # Generate report button
            if st.button("🚀 Generate Data Report", type="primary", use_container_width=True):
                with st.spinner("Analyzing your data..."):
                    # Run analysis
                    overview = get_dataset_overview(df)
                    quality = get_data_quality(df)
                    stats = get_statistical_summary(df)
                    corr_matrix, correlations = get_correlation_matrix(df)
                    
                with st.spinner("Creating visualizations..."):
                    visuals = generate_all_visuals(df)
                
                with st.spinner("Generating insights..."):
                    insights = generate_all_insights(overview, quality, stats, correlations, df)
                
                # Store in session state
                st.session_state['report_data'] = {
                    'overview': overview,
                    'quality': quality,
                    'stats': stats,
                    'visuals': visuals,
                    'insights': insights,
                    'correlations': correlations
                }
                st.session_state['report_generated'] = True
                st.rerun()
        
        except pd.errors.EmptyDataError:
            st.error("❌ The uploaded file is empty or corrupted.")
        except pd.errors.ParserError:
            st.error("❌ Unable to parse the CSV file. Please ensure it's a valid CSV format.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
    
    # Display report if generated
    if st.session_state.get('report_generated') and 'report_data' in st.session_state:
        data = st.session_state['report_data']
        
        st.markdown("---")
        st.markdown("## 📈 Analysis Report")
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🔍 Data Quality", "📉 Statistics", "📈 Visualizations", "💡 Insights"
        ])
        
        with tab1:
            st.markdown("### Dataset Overview")
            overview = data['overview']
            
            cols = st.columns(5)
            metrics = [
                ("Total Rows", f"{overview['rows']:,}"),
                ("Total Columns", overview['columns']),
                ("Numerical", overview['numerical_count']),
                ("Categorical", overview['categorical_count']),
                ("Memory", f"{overview['memory_usage_mb']} MB")
            ]
            for col, (label, value) in zip(cols, metrics):
                col.metric(label, value)
        
        with tab2:
            st.markdown("### Data Quality Analysis")
            quality = data['quality']
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Duplicate Rows", f"{quality['duplicate_rows']:,}", f"{quality['duplicate_percentage']}%")
            col2.metric("Columns with Missing", len(quality['missing_values']))
            col3.metric("Constant Columns", len(quality['constant_columns']))
            
            if quality['missing_values']:
                st.markdown("#### Missing Values by Column")
                missing_df = pd.DataFrame([
                    {'Column': col, 'Missing Count': d['count'], 'Missing %': d['percentage']}
                    for col, d in quality['missing_values'].items()
                ])
                st.dataframe(missing_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.markdown("### Statistical Summary")
            stats = data['stats']
            
            if stats['numerical']:
                st.markdown("#### Numerical Columns")
                num_df = pd.DataFrame(stats['numerical']).T
                num_df.index.name = 'Column'
                st.dataframe(num_df, use_container_width=True)
            
            if stats['categorical']:
                st.markdown("#### Categorical Columns")
                cat_data = []
                for col, d in stats['categorical'].items():
                    top = d['top_values'][0] if d['top_values'] else {'value': 'N/A', 'percentage': 0}
                    cat_data.append({
                        'Column': col,
                        'Unique Values': d['unique_count'],
                        'Top Value': top['value'],
                        'Top Value %': f"{top['percentage']}%"
                    })
                st.dataframe(pd.DataFrame(cat_data), use_container_width=True, hide_index=True)
        
        with tab4:
            st.markdown("### Visualizations")
            visuals = data['visuals']
            
            if visuals['histograms']:
                st.markdown("#### Numerical Distributions")
                cols = st.columns(2)
                for i, hist in enumerate(visuals['histograms']):
                    with cols[i % 2]:
                        st.image(f"data:image/png;base64,{hist['image']}", 
                                caption=hist['column'], use_container_width=True)
            
            if visuals['bar_charts']:
                st.markdown("#### Categorical Distributions")
                cols = st.columns(2)
                for i, chart in enumerate(visuals['bar_charts']):
                    with cols[i % 2]:
                        st.image(f"data:image/png;base64,{chart['image']}", 
                                caption=chart['column'], use_container_width=True)
            
            if visuals['correlation_heatmap']:
                st.markdown("#### Correlation Heatmap")
                st.image(f"data:image/png;base64,{visuals['correlation_heatmap']}", 
                        use_container_width=True)
        
        with tab5:
            st.markdown("### Business Insights")
            for insight in data['insights']:
                css_class = "insight-card"
                if "⚠" in insight:
                    css_class += " insight-warning"
                elif "✓" in insight:
                    css_class += " insight-success"
                st.markdown(f'<div class="{css_class}">{insight}</div>', unsafe_allow_html=True)
        
        # Download section
        st.markdown("---")
        st.markdown("### 📥 Download Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate HTML report
            html_report = generate_html_report(
                data['overview'], data['quality'], data['stats'],
                data['visuals'], data['insights']
            )
            st.download_button(
                label="📄 Download HTML Report",
                data=html_report,
                file_name=f"data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col2:
            st.info("💡 Open the HTML report in your browser for the best viewing experience.")


if __name__ == "__main__":
    main()
