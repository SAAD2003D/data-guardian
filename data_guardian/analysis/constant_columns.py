import pandas as pd

# --- End of discouraged sys.path manipulation ---
from ..core.DataIssue import DataIssue # Corrected import path assuming core is sibling of analysis

def detect_constant_columns(df):
    """
    Detects columns where all non-null values are the same.
    """
    issues = []
    if df is None or df.empty:
        return issues

    for col_name in df.columns:
        # nunique() by default does not count NaN. If a column is all NaN, it's a missing value issue.
        # If it has one unique value AND some NaNs, it's still constant among non-NaNs.
        # If a column is entirely NaN, nunique() is 0. If it has one value and NaNs, nunique() is 1.
        # If it is truly constant (all same non-null value), nunique() is 1.
        
        unique_values = df[col_name].dropna().unique() # Get unique non-NaN values

        if len(unique_values) == 1:
            # This column has only one unique non-null value
            constant_value = unique_values[0]
            description = f"Column '{col_name}' contains only one unique non-null value: '{constant_value}'."
            issue = DataIssue(
                issue_type="ConstantColumn",
                column_name=col_name,
                description=description,
                severity="Medium", # Could be low if intended, medium if potentially problematic
                suggested_action="Verify if this column should be constant. It might carry redundant information or indicate an upstream data issue."
            )
            # Calculate percentage based on number of columns, or consider it a dataset-level structural issue.
            # For now, let's set affected rows to total rows if column is constant.
            issue.set_percentage_metrics(df.shape[0], df.shape[0]) # Affects all rows in terms of this column property
            issues.append(issue)
            # print(f"ConstantColumn issue created: Column: {col_name}, Value: {constant_value}")

    # print(f"Constant column issues found: {len(issues)}")
    return issues