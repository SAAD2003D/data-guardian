import pandas as pd
import sys
import os


# --- End of discouraged sys.path manipulation ---
from ..core.DataIssue import DataIssue

def analyze_string_patterns(df):
    """
    Analyzes string columns for common pattern issues like leading/trailing whitespace
    and mixed casing (basic check).
    """
    issues = []
    if df is None or df.empty:
        return issues
    
    num_rows = df.shape[0]
    if num_rows == 0: return issues

    string_columns = df.select_dtypes(include=['object', 'category']).columns

    for col_name in string_columns:
        # Ensure series is string type for .str accessor, handle NaNs by dropping them for these checks
        # as whitespace or casing isn't relevant for NaN itself.
        valid_strings = df[col_name].dropna().astype(str)
        if valid_strings.empty:
            continue

        # 1. Check for leading/trailing whitespace
        # regex=True is default for contains with complex patterns but good to be explicit
        whitespace_mask = valid_strings.str.contains(r'^\s|\s$', regex=True)
        whitespace_count = whitespace_mask.sum()

        if whitespace_count > 0:
            percentage = (whitespace_count / num_rows) * 100 # Percentage of total rows
            description = f"{whitespace_count} value(s) with leading or trailing whitespace found in column '{col_name}'."
            # Get original indices from df for rows with whitespace
            original_indices_ws = list(df[df[col_name].isin(valid_strings[whitespace_mask])].index)
            
            issue = DataIssue(
                issue_type="LeadingTrailingWhitespace",
                column_name=col_name,
                description=description,
                row_indices=original_indices_ws,
                severity="Low",
                suggested_action="Trim whitespace from values in this column (e.g., using .str.strip())."
            )
            issue.set_percentage_metrics(whitespace_count, len(valid_strings)) # % of non-null strings
            issues.append(issue)
            # print(f"Whitespace issue: {col_name}, Count: {whitespace_count}")

        # 2. Basic check for mixed casing (e.g., "apple", "Apple", "APPLE")
        # This is a simplified check. More robust would involve comparing unique values after lowercasing.
        # If number of unique values decreases significantly after lowercasing, it indicates mixed casing for same semantic value.
        num_unique_original = valid_strings.nunique()
        num_unique_lower = valid_strings.str.lower().nunique()

        if num_unique_original > num_unique_lower and num_unique_lower > 0: # Ensure not just one unique value
            # This suggests some values are distinct only due to case
            description = (f"Column '{col_name}' contains values that differ only by case (e.g., 'Apple' vs 'apple'). "
                           f"Original unique count: {num_unique_original}, Lowercase unique count: {num_unique_lower}.")
            issue = DataIssue(
                issue_type="MixedCaseValues",
                column_name=col_name,
                description=description,
                severity="Medium",
                suggested_action="Standardize casing (e.g., convert all to lowercase or title case) to ensure consistency."
            )
            # This is a column-level property, not easily tied to specific rows without more complex logic
            # We can set affected rows to total valid strings as it impacts the whole column's interpretation
            issue.set_percentage_metrics(len(valid_strings), len(valid_strings))
            issues.append(issue)
            # print(f"MixedCase issue: {col_name}, Unique Original: {num_unique_original}, Unique Lower: {num_unique_lower}")
            
    # print(f"String pattern issues found: {len(issues)}")
    return issues