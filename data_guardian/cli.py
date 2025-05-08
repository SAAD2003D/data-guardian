import argparse
import os
import sys

# Assuming cli.py is in data_guardian and run as `python -m data_guardian.cli ...`
from .core.DatasetProfile import DatasetProfile
from .reporting.html_reporter import HTMLReporter # For HTML
from .reporting.pdf_reporter import PDFReporter   # For PDF


def main():
    parser = argparse.ArgumentParser(description="Data Guardian: Analyze data quality of CSV/Excel files.")
    parser.add_argument("file_path", help="Path to the CSV or Excel file to analyze.")
    parser.add_argument("-n", "--name", help="Optional name for the dataset profile.", default=None)
    parser.add_argument("-t", "--type", help="File type ('csv' or 'excel'). Inferred if not provided.", default=None, choices=['csv', 'excel'])
    parser.add_argument(
        "-o", "--output", 
        help="Output report file name (e.g., report.pdf or report.html). Extension determines format.", 
        default="data_quality_report.pdf" # Default to PDF
    )
    # Add arguments for config file later

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found at '{args.file_path}'")
        sys.exit(1)

    print("Initializing Data Guardian...")
    profile = DatasetProfile(source_path=args.file_path, name=args.name, file_type=args.type)

    if profile.load_data():
        config = { # Example config, load from file later
            'outliers_numerical': {'method': 'iqr', 'threshold': 1.5},
            'custom_null_strings': ["", "na", "n/a", "null", "none", "--", "missing", "#N/A"]
        }
        # If your analyze_null_values and find_numerical_outliers are adapted
        # to take config, pass it here. For now, assuming they use defaults or
        # DatasetProfile.run_analysis handles internal config.
        profile.run_analysis() # Pass config=config if run_analysis takes it
        profile.calculate_quality_scores()
        
        # --- Text Report to Console (still useful) ---
        summary = profile.get_summary_report()
        print("\n" + summary)
        print("-" * 70)

        # --- File Based Reporting (HTML or PDF) ---
        output_filename = args.output
        file_ext = os.path.splitext(output_filename)[1].lower()

        if file_ext == ".pdf":
            print(f"Generating PDF report: {output_filename}")
            pdf_reporter = PDFReporter(profile) # It will internally use HTMLReporter
            if not pdf_reporter.generate_pdf_report(output_path=output_filename):
                print("Failed to generate PDF report.")
        elif file_ext == ".html":
            print(f"Generating HTML report: {output_filename}")
            html_reporter = HTMLReporter(profile)
            if not html_reporter.save_html_report(output_path=output_filename):
                print("Failed to generate HTML report.")
        else:
            print(f"Unsupported report output format: {file_ext}. Supported: .pdf, .html")
            print("Defaulting to console output only.")

    else:
        print(f"Could not proceed with analysis for {args.file_path}.")
        sys.exit(1)

if __name__ == "__main__":
    main()