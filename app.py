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
FOLDER_ICON = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 8px;">
<path d="M3 8.2C3 7.07989 3 6.51984 3.21799 6.09202C3.40973 5.71569 3.71569 5.40973 4.09202 5.21799C4.51984 5 5.0799 5 6.2 5H9.67452C10.1637 5 10.4083 5 10.6385 5.05526C10.8425 5.10425 11.0376 5.18506 11.2166 5.29472C11.4184 5.4184 11.5914 5.59135 11.9373 5.93726L12.0627 6.06274C12.4086 6.40865 12.5816 6.5816 12.7834 6.70528C12.9624 6.81494 13.1575 6.89575 13.3615 6.94474C13.5917 7 13.8363 7 14.3255 7H17.8C18.9201 7 19.4802 7 19.908 7.21799C20.2843 7.40973 20.5903 7.71569 20.782 8.09202C21 8.51984 21 9.0799 21 10.2V15.8C21 16.9201 21 17.4802 20.782 17.908C20.5903 18.2843 20.2843 18.5903 19.908 18.782C19.4802 19 18.9201 19 17.8 19H6.2C5.07989 19 4.51984 19 4.09202 18.782C3.71569 18.5903 3.40973 18.2843 3.21799 17.908C3 17.4802 3 16.9201 3 15.8V8.2Z" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

DOWNLOAD_ICON = '''<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 8px;">
<path d="M3 12.3V19.3C3 20.4046 3.89543 21.3 5 21.3H19C20.1046 21.3 21 20.4046 21 19.3V12.3" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<polyline points="7.9 12.3 12 16.3 16.1 12.3" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
<line x1="12" y1="2.7" x2="12" y2="14.2" stroke="#4F46E5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''


# Page configuration
st.set_page_config(
    page_title="Data Report Generator",
    page_icon="assets/favicon.ico",
    initial_sidebar_state="collapsed"
)

# Clean CSS for light theme
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Headers */
    .main-header {
        font-size: 1.875rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 2rem;
        line-height: 1.5;
    }
    
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.75rem;
    }
    
    /* Success/Error messages */
    .success-box {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 8px;
        padding: 12px 16px;
        color: #065F46;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 12px 16px;
        color: #991B1B;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Insight cards - improved */
    .insights-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .insight-item {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px 20px;
        font-size: 0.9rem;
        line-height: 1.7;
        color: #374151;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        transition: box-shadow 0.15s ease;
    }
    
    .insight-item:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .insight-icon {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        margin-top: 2px;
    }
    
    .insight-item.info .insight-icon {
        background: #EEF2FF;
        color: #4F46E5;
    }
    
    .insight-item.warning .insight-icon {
        background: #FEF3C7;
        color: #D97706;
    }
    
    .insight-item.success .insight-icon {
        background: #D1FAE5;
        color: #059669;
    }
    
    .insight-content {
        flex: 1;
    }
    
    .insight-item.warning {
        border-color: #FDE68A;
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
    }
    
    .insight-item.success {
        border-color: #A7F3D0;
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
    }
    
    .insight-item.info {
        border-color: #C7D2FE;
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
    }
    
    /* Info box */
    .info-box {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 12px 16px;
        color: #6B7280;
        font-size: 0.875rem;
    }
    
    /* Divider */
    .divider {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 1.5rem 0;
    }
    
    /* Hide Streamlit elements */
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
    st.markdown(f'<p class="section-title">{FOLDER_ICON}Upload Your Data</p>', unsafe_allow_html=True)
    
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
                st.markdown('<div class="error-box">The uploaded CSV file is empty. Please upload a file with data.</div>', unsafe_allow_html=True)
                return
            
            # Display file info
            st.markdown(f'<div class="success-box">Successfully loaded: {uploaded_file.name}</div>', unsafe_allow_html=True)
            
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
            
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            
            # Generate report button
            if st.button("Generate Data Report", type="primary", use_container_width=True):
                with st.spinner("Analyzing your data..."):
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
            st.markdown('<div class="error-box">The uploaded file is empty or corrupted.</div>', unsafe_allow_html=True)
        except pd.errors.ParserError:
            st.markdown('<div class="error-box">Unable to parse the CSV file. Please ensure it is a valid CSV format.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">An error occurred: {str(e)}</div>', unsafe_allow_html=True)
    
    # Display report if generated
    if st.session_state.get('report_generated') and 'report_data' in st.session_state:
        data = st.session_state['report_data']
        
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.subheader("Analysis Report")
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Data Quality", "Statistics", "Visualizations", "Insights"
        ])
        
        with tab1:
            st.markdown("**Dataset Overview**")
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
            st.markdown("**Data Quality Analysis**")
            quality = data['quality']
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Duplicate Rows", f"{quality['duplicate_rows']:,}", f"{quality['duplicate_percentage']}%")
            col2.metric("Columns with Missing", len(quality['missing_values']))
            col3.metric("Constant Columns", len(quality['constant_columns']))
            
            if quality['missing_values']:
                st.markdown("**Missing Values by Column**")
                missing_df = pd.DataFrame([
                    {'Column': col, 'Missing Count': d['count'], 'Missing %': d['percentage']}
                    for col, d in quality['missing_values'].items()
                ])
                st.dataframe(missing_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.markdown("**Statistical Summary**")
            stats = data['stats']
            
            if stats['numerical']:
                st.markdown("**Numerical Columns**")
                num_df = pd.DataFrame(stats['numerical']).T
                num_df.index.name = 'Column'
                st.dataframe(num_df, use_container_width=True)
            
            if stats['categorical']:
                st.markdown("**Categorical Columns**")
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
            st.markdown("**Visualizations**")
            visuals = data['visuals']
            
            if visuals['histograms']:
                st.markdown("**Numerical Distributions**")
                cols = st.columns(2)
                for i, hist in enumerate(visuals['histograms']):
                    with cols[i % 2]:
                        st.image(f"data:image/png;base64,{hist['image']}", 
                                caption=hist['column'], use_container_width=True)
            
            if visuals['bar_charts']:
                st.markdown("**Categorical Distributions**")
                cols = st.columns(2)
                for i, chart in enumerate(visuals['bar_charts']):
                    with cols[i % 2]:
                        st.image(f"data:image/png;base64,{chart['image']}", 
                                caption=chart['column'], use_container_width=True)
            
            if visuals['correlation_heatmap']:
                st.markdown("**Correlation Heatmap**")
                st.image(f"data:image/png;base64,{visuals['correlation_heatmap']}", 
                        use_container_width=True)
        
        with tab5:
            st.markdown("**Business Insights**")
            
            insights_html = '<div class="insights-container">'
            for insight in data['insights']:
                # Clean insight text
                clean_insight = insight
                for emoji in ["⚠ ", "⚠", "✓ ", "✓", "📊 ", "📊"]:
                    clean_insight = clean_insight.replace(emoji, "")
                
                # Classify and assign icon
                if "missing" in insight.lower() or "imbalanced" in insight.lower() or "skewed" in insight.lower() or "variability" in insight.lower():
                    css_class = "insight-item warning"
                    icon = "!"
                elif "No " in insight or "unique" in insight.lower() or "complete" in insight.lower():
                    css_class = "insight-item success"
                    icon = "✓"
                elif "correlation" in insight.lower():
                    css_class = "insight-item info"
                    icon = "~"
                else:
                    css_class = "insight-item info"
                    icon = "i"
                
                insights_html += f'''
                <div class="{css_class}">
                    <div class="insight-icon">{icon}</div>
                    <div class="insight-content">{clean_insight}</div>
                </div>'''
            
            insights_html += '</div>'
            st.markdown(insights_html, unsafe_allow_html=True)
        
        # Download section
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(f'<p class="section-title">{DOWNLOAD_ICON}Download Report</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
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
            st.markdown('<div class="info-box">Open the HTML report in your browser for the best viewing experience.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
