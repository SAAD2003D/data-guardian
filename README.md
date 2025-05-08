# Data Guardian 🛡️

[![PyPI version](https://badge.fury.io/py/data-guardian.svg)](https://badge.fury.io/py/data-guardian)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/data-guardian)](https://pypi.org/project/data-guardian/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Update with your actual license -->
<!-- Add other badges if you have them (e.g., build status, test coverage) -->
<!-- [![Build Status](https://travis-ci.org/YOUR_USERNAME/data-guardian.svg?branch=main)](https://travis-ci.org/YOUR_USERNAME/data-guardian) -->
<!-- [![Coverage Status](https://coveralls.io/repos/github/YOUR_USERNAME/data-guardian/badge.svg?branch=main)](https://coveralls.io/github/YOUR_USERNAME/data-guardian?branch=main) -->

Data Guardian is a Python library designed to meticulously analyze the quality of your tabular datasets (CSV and Excel). It provides a comprehensive audit, a clear scoring system, and generates detailed reports in text, HTML, and PDF formats, empowering you to trust and effectively utilize your data.

Whether you're a data scientist, analyst, researcher, or civic tech worker, Data Guardian helps you quickly identify and understand issues like missing values, inconsistencies, outliers, and duplicates before you dive into deeper analysis, visualization, or machine learning.

## ✨ Key Features

*   **Comprehensive Data Profiling:** Identifies a wide range of common data quality issues:
    *   Missing Values (NaNs)
    *   Suspicious Null-like Strings (e.g., "NA", "Null", "", "--")
    *   Constant Columns (columns with only one unique value)
    *   Duplicated Rows
    *   Leading/Trailing Whitespace in string values
    *   Mixed Case Values (e.g., "Apple" vs "apple")
    *   Potential Numeric Types (object columns that appear fully numeric)
    *   Mixed Data Types within object columns
    *   Numerical Outliers (using IQR or Z-score methods)
    *   Categorical Outliers (rare categories)
*   **Intuitive Quality Scoring:** Generates scores 0/100 for:
    *   Completeness
    *   Uniqueness
    *   Consistency
    *   Validity
    *   An Overall Quality Score
*   **Detailed Reporting:** Produces human-readable reports in multiple formats:
    *   Console Text Summary
    *   HTML Report (with basic styling, suitable for sharing)
    *   PDF Report (for archival and formal documentation)
*   **Easy-to-Use API:** Simple Python interface to integrate into your data workflows.
*   **Command-Line Interface (CLI):** Quickly analyze datasets directly from your terminal.
*   **File Support:** Natively handles CSV and Excel (`.xls`, `.xlsx`) files.
*   **Configurable Analysis:** (Future - ability to tune thresholds and checks).

## 🚀 Installation

You can install Data Guardian using pip. Python 3.8 or higher is required.

```bash
pip install data-guardian==0.1.0

```
## ⚡ Quickstart
```bash 
from data_guardian import DatasetProfile, PDFReporter # Or HTMLReporter

# 1. Specify the path to your data file
file_path = "path/to/your/dataset.csv" # Or "path/to/your/dataset.xlsx"
# For example, if you downloaded the comprehensive_test_data.csv from the project:
# file_path = "data/comprehensive_test_data.csv"


# 2. Create a DatasetProfile instance
# The name is optional; if not provided, it uses the filename.
# The file_type ('csv' or 'excel') is also optional and will be inferred from the extension.
profile = DatasetProfile(source_path=file_path, name="My Sample Analysis")

# 3. Load the data
if profile.load_data():
    print(f"Successfully loaded: {profile.name}")

    # 4. Run all available data quality analyses
    # You can pass a configuration dictionary if needed for specific analyses,
    # e.g., custom_null_strings or outlier parameters.
    # analysis_config = {
    #     'custom_null_strings': ["N/A", "-", "Not Available"],
    #     'outliers_numerical': {'method': 'zscore', 'threshold': 3.0}
    # }
    # profile.run_analysis(config=analysis_config) # Pass config if using custom settings
    profile.run_analysis() # Uses default settings if config is not passed
    print(f"Analysis complete. Issues found: {len(profile.issues_found)}")

    # 5. Calculate quality scores based on the analysis
    profile.calculate_quality_scores()
    if profile.quality_score:
        print(f"Overall Quality Score: {profile.quality_score.overall_score:.2f}/100")

    # 6. Get a text summary report (printed to console)
    print("\n--- Text Summary Report ---")
    print(profile.get_summary_report())

    # 7. Generate a PDF report
    print("\n--- Generating PDF Report ---")
    pdf_reporter = PDFReporter(profile)
    pdf_output_path = "data_guardian_report.pdf"
    if pdf_reporter.generate_pdf_report(output_path=pdf_output_path):
        print(f"PDF report saved to: {pdf_output_path}")
    else:
        print("Failed to generate PDF report.")

    # # Alternatively, generate an HTML report
    # from data_guardian import HTMLReporter
    # print("\n--- Generating HTML Report ---")
    # html_reporter = HTMLReporter(profile)
    # html_output_path = "data_guardian_report.html"
    # if html_reporter.save_html_report(output_path=html_output_path):
    #     print(f"HTML report saved to: {html_output_path}")
    # else:
    #     print("Failed to generate HTML report.")

else:
    print(f"Failed to load data from: {file_path}")

``` 
## Command-Line Interface (CLI)
```bash
data-guardian-cli path/to/your/dataset.csv -o quality_report.pdf
``` 
## CLI examples:

```bash
# Analyze a CSV and generate a PDF report (default output name)
data-guardian-cli my_data.csv

# Analyze an Excel file and generate an HTML report with a custom name
data-guardian-cli financial_data.xlsx -o financial_audit.html --name "Financial Audit Q1"

# Analyze a CSV, specifying its type, and output to a custom PDF name
data-guardian-cli sales_records -t csv -o sales_quality.pdf --name "Sales Records"
``` 

## 🤝 Contributing:
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
If you have suggestions for adding or removing projects, feel free to open an issue to discuss it, or directly create a pull request after you've first forked the repo and created a branch from main.

* 1-Fork the Project (Click the "Fork" button on the GitHub repository page: https://github.com/SAAD2003D/data-guardian) 
* 2-Create your Feature Branch (git checkout -b feature/AmazingFeature)
* 3-Commit your Changes (git commit -m 'Add some AmazingFeature')
* 4-Push to the Branch (git push origin feature/AmazingFeature)
* 5-Open a Pull Request


## 📧 Contact
saad fikri  – fsaad1929@gmail.com  


