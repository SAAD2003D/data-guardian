import pandas as pd
from datetime import datetime
import os # For sys.path, consider better alternatives for package structure

# --- This sys.path manipulation is generally discouraged. ---
# --- It's better to run your scripts from the project root, ---
# --- or install your package in editable mode. ---
# --- For this example, I'll keep it to match user's structure temporarily. ---


from ..io.loaders import load_dataset # io is now a sibling directory
from .DataIssue import DataIssue # core is current directory
# Analysis functions will be imported within run_analysis or at the top of the file
from ..analysis import missing_values, constant_columns, duplicated_rows, string_patterns, data_types, outliers

class DatasetProfile:
    def __init__(self, source_path, name=None, file_type=None):
        self.source_path = source_path
        self.name = name if name else os.path.basename(source_path)
        self.file_type = file_type # Can be 'csv' or 'excel', or None to infer
        self.load_timestamp = None
        self.raw_data = None
        self.issues_found = [] # List of DataIssue objects
        self.quality_score = None # Will be a QualityScore object

    def load_data(self):
        print(f"Attempting to load dataset: {self.name} from {self.source_path}")
        self.raw_data = load_dataset(self.source_path, self.file_type)
        if self.raw_data is not None:
            self.load_timestamp = datetime.now()
            print(f"Dataset '{self.name}' loaded successfully. Shape: {self.raw_data.shape}")
            return True
        else:
            print(f"Failed to load dataset '{self.name}'.")
            return False

    def run_analysis(self, config=None): # Config for thresholds, etc.
        if self.raw_data is None:
            print("Error: Data not loaded. Cannot run analysis.")
            return

        print(f"\n--- Running Analysis for {self.name} ---")
        self.issues_found = [] # Reset issues

        # 1. Missing Values (including custom null strings)
        mv_issues = missing_values.analyze_null_values(self.raw_data)
        self.issues_found.extend(mv_issues)
        print(f"Found {len(mv_issues)} missing value/suspicious string related issues.")

        # 2. Constant Columns
        cc_issues = constant_columns.detect_constant_columns(self.raw_data)
        self.issues_found.extend(cc_issues)
        print(f"Found {len(cc_issues)} constant column issues.")

        # 3. Duplicated Rows
        # (Make sure duplicated_rows.py exists and function is named detect_duplicated_rows)
        dr_issues = duplicated_rows.detect_duplicated_rows(self.raw_data)
        self.issues_found.extend(dr_issues)
        print(f"Found {len(dr_issues)} duplicated row issues.")

        # 4. String Patterns (e.g., whitespace)
        sp_issues = string_patterns.analyze_string_patterns(self.raw_data)
        self.issues_found.extend(sp_issues)
        print(f"Found {len(sp_issues)} string pattern issues.")
        
        # 5. Data Types (e.g., inconsistent types in object columns)
        dt_issues = data_types.analyze_data_types(self.raw_data)
        self.issues_found.extend(dt_issues)
        print(f"Found {len(dt_issues)} data type related issues.")

        # 6. Outliers (Numerical)
        # You might want to pass configuration for outlier detection methods/thresholds
        outlier_config = config.get('outliers_numerical', {'method': 'iqr', 'threshold': 1.5}) if config else {'method': 'iqr', 'threshold': 1.5}
        no_issues = outliers.find_numerical_outliers(self.raw_data,
                                                     method=outlier_config['method'],
                                                     threshold=outlier_config['threshold'])
        self.issues_found.extend(no_issues)
        print(f"Found {len(no_issues)} numerical outlier issues.")

        # 7. Outliers (Categorical - optional, can be added)
        # cat_outlier_config = config.get('outliers_categorical', {'threshold': 0.01}) if config else {'threshold': 0.01}
        # co_issues = outliers.find_categorical_outliers(self.raw_data, threshold=cat_outlier_config['threshold'])
        # self.issues_found.extend(co_issues)
        # print(f"Found {len(co_issues)} categorical outlier issues.")

        print(f"--- Analysis Complete for {self.name}. Total issues found: {len(self.issues_found)} ---")

    def calculate_quality_scores(self):
        if not self.issues_found and self.raw_data is None:
            print("Run analysis first and ensure data is loaded.")
            return
        if self.raw_data is None: # Should not happen if issues_found is populated, but good check
            print("Data not loaded. Cannot calculate scores.")
            return

        from .QualityScore import QualityScore # Local import
        self.quality_score = QualityScore(self.raw_data, self.issues_found)
        self.quality_score.calculate_all_scores()
        print("Quality scores calculated.")

    def get_summary_report(self):
        if self.raw_data is None:
            return "Dataset not loaded."

        report_lines = []
        report_lines.append(f"===== Data Quality Audit Report for: {self.name} =====")
        report_lines.append(f"Source: {self.source_path}")
        report_lines.append(f"Loaded at: {self.load_timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.load_timestamp else 'N/A'}")
        report_lines.append(f"Dimensions: {self.raw_data.shape[0]} rows, {self.raw_data.shape[1]} columns")
        report_lines.append("-" * 70)

        if not self.issues_found:
            report_lines.append("No data quality issues found (based on current checks).")
        else:
            report_lines.append(f"Total Issues Found: {len(self.issues_found)}")
            # Group issues by type for better readability
            issues_by_type = {}
            for issue in self.issues_found:
                issues_by_type.setdefault(issue.issue_type, []).append(issue)

            for issue_type, issues_list in issues_by_type.items():
                report_lines.append(f"\n--- {issue_type} ({len(issues_list)} occurrences) ---")
                for i, issue in enumerate(issues_list[:5]): # Show first 5 of each type for brevity
                    report_lines.append(f"  - Column: '{issue.column_name}', Desc: {issue.description}, Severity: {issue.severity}, Affected: {issue.percentage_affected:.2f}%")
                if len(issues_list) > 5:
                    report_lines.append(f"    ... and {len(issues_list) - 5} more {issue_type} issues.")
        report_lines.append("-" * 70)

        if self.quality_score:
            report_lines.append("\n===== Quality Scores =====")
            report_lines.append(self.quality_score.get_summary())
        else:
            report_lines.append("\nQuality scores not yet calculated.")
        report_lines.append("=" * 70)
        return "\n".join(report_lines)