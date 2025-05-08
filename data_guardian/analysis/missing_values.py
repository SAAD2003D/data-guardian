import pandas as pd

# --- End of discouraged sys.path manipulation ---
from ..core.DataIssue import DataIssue

def analyze_null_values(df, custom_null_strings=None):
    """
    Analyzes DataFrame for both standard (NaN) missing values and custom string-defined nulls.
    """
    issues = []
    if df is None or df.empty:
        return issues

    num_rows = df.shape[0]
    if num_rows == 0: return issues


    # 1. Standard NaN missing values
    nan_counts = df.isnull().sum()
    for column_name, null_count in nan_counts.items():
        if null_count > 0:
            percentage = (null_count / num_rows) * 100
            description = f"{null_count} standard missing values (NaN) found in column '{column_name}'."
            issue = DataIssue(
                issue_type="MissingValue",
                column_name=column_name,
                description=description,
                severity="High" if percentage > 50 else ("Medium" if percentage > 10 else "Low"),
                suggested_action="Consider imputation (mean, median, mode, model-based) or row deletion if appropriate."
            )
            issue.set_percentage_metrics(null_count, num_rows)
            issues.append(issue)
            # print(f"MissingValue issue: {column_name}, Count: {null_count}, %: {percentage:.2f}")

    # 2. Custom null-like strings (e.g., "", "NA", "Null")
    if custom_null_strings is None:
        custom_null_strings = ["", "na", "n/a", "null", "none", "--", "missing"] # Default list
    
    # Make the check case-insensitive by converting both series and list to lower
    custom_null_strings_lower = [str(s).lower() for s in custom_null_strings]

    for col_name in df.select_dtypes(include=['object', 'category']).columns: # Only check string-like columns
        # Ensure column is string type before .str accessor, handle potential existing NaNs carefully
        # .astype(str) converts NaNs to "nan" string, which might be in custom_null_strings_lower
        # A safer way for .str.lower() is to dropna first if we only want to check actual strings
        
        # Create a boolean series for matching custom nulls
        try:
            # Handle actual NaNs: they won't match .str.lower() and .isin()
            # We are looking for strings that *look like* nulls, not actual NaNs (already caught above)
            series_lower = df[col_name].dropna().astype(str).str.lower()
            suspicious_mask = series_lower.isin(custom_null_strings_lower)
            suspicious_count = suspicious_mask.sum()

            if suspicious_count > 0:
                percentage = (suspicious_count / num_rows) * 100
                # Find which specific suspicious strings were found
                found_values = series_lower[suspicious_mask].unique()
                description = (f"{suspicious_count} suspicious null-like strings (e.g., {', '.join(found_values[:3])}"
                               f"{'...' if len(found_values) > 3 else ''}) found in column '{column_name}'.")
                issue = DataIssue(
                    issue_type="SuspiciousValue", # Differentiate from standard NaN
                    column_name=col_name,
                    description=description,
                    value_found=list(found_values),
                    severity="Medium", # Usually indicates data entry issues
                    suggested_action="These strings might represent missing data. Consider standardizing them to NaN during data loading or cleaning."
                )
                issue.set_percentage_metrics(suspicious_count, num_rows)
                issues.append(issue)
                # print(f"SuspiciousValue issue: {col_name}, Count: {suspicious_count}, Values: {list(found_values)}")
        except Exception as e:
            print(f"Error processing column {col_name} for suspicious nulls: {e}")


    # print(f"Missing value / suspicious string issues found: {len(issues)}")
    return issues