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


# SVG Icons (inline)
FOLDER_ICON = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3 8.2C3 7.07989 3 6.51984 3.21799 6.09202C3.40973 5.71569 3.71569 5.40973 4.09202 5.21799C4.51984 5 5.0799 5 6.2 5H9.67452C10.1637 5 10.4083 5 10.6385 5.05526C10.8425 5.10425 11.0376 5.18506 11.2166 5.29472C11.4184 5.4184 11.5914 5.59135 11.9373 5.93726L12.0627 6.06274C12.4086 6.40865 12.5816 6.5816 12.7834 6.70528C12.9624 6.81494 13.1575 6.89575 13.3615 6.94474C13.5917 7 13.8363 7 14.3255 7H17.8C18.9201 7 19.4802 7 19.908 7.21799C20.2843 7.40973 20.5903 7.71569 20.782 8.09202C21 8.51984 21 9.0799 21 10.2V15.8C21 16.9201 21 17.4802 20.782 17.908C20.5903 18.2843 20.2843 18.5903 19.908 18.782C19.4802 19 18.9201 19 17.8 19H6.2C5.07989 19 4.51984 19 4.09202 18.782C3.71569 18.5903 3.40973 18.2843 3.21799 17.908C3 17.4802 3 16.9201 3 15.8V8.2Z" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

DOWNLOAD_ICON = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3 12.3V19.3C3 20.4046 3.89543 21.3 5 21.3H19C20.1046 21.3 21 20.4046 21 19.3V12.3" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<polyline points="7.9 12.3 12 16.3 16.1 12.3" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
<line x1="12" y1="2.7" x2="12" y2="14.2" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''


# Page configuration
st.set_page_config(
    page_title="Data Report Generator",
    page_icon=None,
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional light theme with improved typography
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Force light theme */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Global typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-header svg {
        flex-shrink: 0;
    }
    
    /* Card styling */
    .info-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #6B7280;
        font-size: 0.875rem;
        line-height: 1.5;
    }
    
    /* Success message */
    .success-msg {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #166534;
        font-weight: 500;
        font-size: 0.875rem;
        margin-bottom: 1.5rem;
    }
    
    /* Error message */
    .error-msg {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #991B1B;
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    /* Insight cards */
    .insight-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 3px solid #6366F1;
        border-radius: 6px;
        padding: 0.875rem 1rem;
        margin-bottom: 0.625rem;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #374151;
    }
    
    .insight-warning {
        border-left-color: #F59E0B;
        background: #FFFBEB;
    }
    
    .insight-success {
        border-left-color: #10B981;
        background: #F0FDF4;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: #4F46E5;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 0.875rem;
        border-radius: 8px;
        transition: all 0.15s ease;
        letter-spacing: 0.01em;
    }
    
    .stButton > button:hover {
        background: #4338CA;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    }
    
    .stButton > button:active {
        transform: translateY(1px);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: #FFFFFF;
        color: #4F46E5;
        border: 1px solid #4F46E5;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        font-size: 0.875rem;
        border-radius: 8px;
    }
    
    .stDownloadButton > button:hover {
        background: #EEF2FF;
        border-color: #4338CA;
        color: #4338CA;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #F3F4F6;
        padding: 0.25rem;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.8125rem;
        color: #6B7280;
        border-radius: 6px;
        padding: 0.5rem 0.875rem;
        height: auto;
    }
    
    .stTabs [aria-selected="true"] {
        background: #FFFFFF;
        color: #111827;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 0.875rem;
        color: #374151;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #E5E7EB;
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    /* Divider */
    .section-divider {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 1.5rem 0;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 2px dashed #D1D5DB;
        border-radius: 10px;
        padding: 0;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #4F46E5;
        background: #FAFAFE;
    }
    
    [data-testid="stFileUploaderDropzone"] {
        background: transparent;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Section title */
    h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 1rem;
    }
    
    h4 {
        font-size: 0.9375rem;
        font-weight: 600;
        color: #374151;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
    st.markdown('<h1 class="main-header">Automated Data Report Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload a CSV file and instantly generate a comprehensive, business-ready data report.</p>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown(f'<p class="section-header">{FOLDER_ICON} Upload Your Data</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload any CSV file to generate an automated analysis report",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            df = pd.read_csv(uploaded_file)
            
            if df.empty:
                st.markdown('<div class="error-msg">The uploaded CSV file is empty. Please upload a file with data.</div>', unsafe_allow_html=True)
                return
            
            # Display file info
            st.markdown(f'<div class="success-msg">Successfully loaded: {uploaded_file.name}</div>', unsafe_allow_html=True)
            
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
            with st.expander("Preview Data (First 10 Rows)", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Column info
            with st.expander("Column Information"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null Count': df.count().values,
                    'Null Count': df.isnull().sum().values
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Generate report button
            if st.button("Generate Data Report", type="primary", use_container_width=True):
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
            st.markdown('<div class="error-msg">The uploaded file is empty or corrupted.</div>', unsafe_allow_html=True)
        except pd.errors.ParserError:
            st.markdown('<div class="error-msg">Unable to parse the CSV file. Please ensure it is a valid CSV format.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-msg">An error occurred: {str(e)}</div>', unsafe_allow_html=True)
    
    # Display report if generated
    if st.session_state.get('report_generated') and 'report_data' in st.session_state:
        data = st.session_state['report_data']
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("## Analysis Report")
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Data Quality", "Statistics", "Visualizations", "Insights"
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
                # Classify and clean insight text
                css_class = "insight-card"
                clean_insight = insight
                
                # Remove emoji prefixes
                for emoji in ["⚠ ", "⚠", "✓ ", "✓", "📊 ", "📊"]:
                    clean_insight = clean_insight.replace(emoji, "")
                
                # Classify by content
                if "missing" in insight.lower() or "may" in insight.lower() or "imbalanced" in insight.lower():
                    css_class += " insight-warning"
                elif "No " in insight or "unique" in insight.lower() or "complete" in insight.lower():
                    css_class += " insight-success"
                    
                st.markdown(f'<div class="{css_class}">{clean_insight}</div>', unsafe_allow_html=True)
        
        # Download section
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(f'<p class="section-header">{DOWNLOAD_ICON} Download Report</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate HTML report
            html_report = generate_html_report(
                data['overview'], data['quality'], data['stats'],
                data['visuals'], data['insights']
            )
            st.download_button(
                label="Download HTML Report",
                data=html_report,
                file_name=f"data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col2:
            st.markdown('<div class="info-card">Open the HTML report in your browser for the best viewing experience.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
