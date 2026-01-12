# Automated Data Report Generator

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

A Streamlit-based Python tool that converts raw CSV files into business-ready data reports with automated insights and visualizations.

**[Live Demo](https://automated-data-report-generator-ffzfvurwehseniu9uk5xsp.streamlit.app/)**

---

## Problem

When onboarding new datasets, data teams and engineers often spend hours writing repetitive exploratory analysis code to assess data quality, understand distributions, and identify key relationships. This slows down decision-making and leads to inconsistent reporting.

---

## Solution

This application automates the initial data assessment process. By uploading a CSV file, users instantly receive a structured, readable data report covering data quality checks, statistical summaries, visual insights, and plain-English observations suitable for business and technical stakeholders.

---

## Features

- CSV upload with instant dataset preview and schema overview
- Automated data quality checks (missing values, duplicates, constant columns)
- Statistical summaries for numerical and categorical features
- Visual insights including distributions and correlation analysis
- Auto-generated plain-English observations highlighting potential data issues and patterns
- One-click export of a business-ready HTML report

---

## How to Run

```bash
git clone https://github.com/siddharth-narigra/automated-data-report-generator
cd automated-data-report-generator
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Example Output

The generated report includes:

- Dataset shape and column type breakdown
- Missing value percentages by column
- Summary statistics (mean, median, standard deviation) for numerical features
- Frequency analysis for categorical features
- Correlation matrix with flagged strong relationships
- Observations such as:
  - "Column Age contains 27% missing values and may require imputation."
  - "A strong correlation is detected between Feature A and Feature B."

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

Built a Python-based internal data reporting tool that automates CSV analysis and generates business-ready HTML reports with insights and visualizations, reducing manual exploratory analysis time by approximately 80%.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
