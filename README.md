# Automated Data Report Generator

A Streamlit application that converts CSV files into professional data reports with statistics, visualizations, and actionable insights.

---

## Problem

Data teams spend significant time on repetitive exploratory analysis when onboarding new datasets. Manual inspection of data quality, distributions, and correlations delays decision-making and introduces inconsistency.

---

## Solution

This tool automates the initial data assessment process. Users upload a CSV file and receive a structured report covering data quality, statistical summaries, visual distributions, and plain-English observations within seconds.

---

## Features

- Single-file CSV upload with instant dataset preview
- Automated data quality analysis (missing values, duplicates, constant columns)
- Statistical summaries for numerical and categorical columns
- Auto-generated visualizations (histograms, bar charts, correlation heatmap)
- Plain-English business insights based on data patterns
- One-click HTML report export

---

## How to Run

```
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 in a browser.

---

## Example Output

The generated report includes:
- Dataset shape and column type breakdown
- Missing value percentages by column
- Mean, median, standard deviation for numerical fields
- Top category frequencies for categorical fields
- Correlation matrix with flagged strong relationships
- Observations such as "Column X has 27% missing values" or "Strong correlation detected between A and B"

---

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib / Seaborn
- Streamlit
- Jinja2

---

## Highlight

Built an internal data reporting tool that automates CSV analysis and generates business-ready HTML reports with insights and visualizations, reducing manual EDA time by approximately 80%.
